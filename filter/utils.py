import re

from django.db.models import Q

class CustomFilter:
    """The custom filter implementation entity

    :param allowed_fields: The list of fields upon which the filter should act
    :param phrase: The query string provided by the user as input
    """

    # either match date or (word or decimal number) or parens
    tokenizer_regex = r"([0-9]{4}-[0-9]{1,2}-[0-9]{1,2}|\b\w*[\.]?\w+\b|[\(\)])"

    word_operators = ["eq", "ne", "lt", "gt", "AND", "OR"]
    all_operators = word_operators + ["(", ")"]
    boolean_operators = ["AND", "OR"]
    precedence = {
        "eq": 3,
        "ne": 3,
        "lt": 3,
        "gt": 3,
        "AND": 2,
        "OR": 1,
    }

    def __init__(self, allowed_fields, phrase):
        self.allowed_fields = allowed_fields
        self.phrase = phrase

    def tokenize(self, source: str) -> list[str]:
        tokens = re.findall(self.tokenizer_regex, source)
        return [token.upper() if token.lower() in ["and", "or"] else token
                for token in tokens]

    def to_postfix(self, tokens: list[str]) -> list[str]:
        """Convert tokens in infix format to tokens in postfix format.

        Conversion is performed using the `Shunting yard` algorithm.
        Reference: https://en.wikipedia.org/wiki/Shunting-yard_algorithm#The_algorithm_in_detail

        :param tokens: list of tokens parsed from source string stored in infix format

        :return: list of tokens converted in postfix format
        """
        operators = []
        stack = []

        for token in tokens:
            if token in self.word_operators:
                while (
                        operators
                        and (
                            operators[-1] in self.all_operators and operators[-1] != "(")
                        and (
                            self.precedence.get(operators[-1]) >= self.precedence.get(token)
                        )
                ):
                    stack.append(operators.pop())

                operators.append(token)

            elif token == "(":
                operators.append(token)

            elif token == ")":
                while True:
                    if len(operators) == 0:
                        break

                    if operators[-1] == "(":
                        operators.pop()
                        break

                    stack.append(operators.pop())

            elif token not in self.word_operators:
                stack.append(token)

        for operator in reversed(operators):
            if operator == "(":
                raise ValueError("Unmatched paranthesis in search phrase.")
            stack.append(operator)

        return stack

    def filter_allowed_fields(
            self,
            allowed_fields: list[str],
            tokens: list[str]
    ) -> list[str]:
        """Filters out tokens which are  not present in allowed_fields.

        :param tokens: list of tokens in postfix format

        :return: filtered list of tokens according to allowed_fields
        """

        token_index_to_remove = set()

        for index, token in enumerate(tokens):
            if token in self.word_operators:
                continue

            # is token a value like `2020-01-01` or `20` i.e.
            # it should not be an operator
            # and not a term like `date`, `distance` etc.
            is_value = index % 3 == 1

            if token not in self.allowed_fields and not is_value:
                token_index_to_remove.update([index, index+1, index+2])

        # new list with the indexes of unallowed fields removed
        tokens = [val for ind, val in enumerate(tokens)
                  if ind not in token_index_to_remove]

        return tokens

    def postfix_to_q(self, tokens: list[str]) -> Q:
        """Convert tokens in postfix format to Q object.

        :param tokens: list of tokens parsed from source string stored in infix format

        :return: Q object with filter conditions from provided `tokens` argument
        """
        stack = []

        for index, token in enumerate(tokens):
            if (token not in self.word_operators):
                stack.append(token)
            elif token in self.word_operators:
                if len(stack) < 2:
                    continue
                last_item = stack.pop()
                second_last_item = stack.pop()

                if token not in self.boolean_operators:
                    if token in ["ne", "eq"]:
                        q_param = {second_last_item: last_item}
                        if token == "ne":
                            stack.append(~Q(**q_param))
                        else:
                            stack.append(Q(**q_param))
                    else:
                        q_query_string = second_last_item + "__" + token
                        q_param = {q_query_string: last_item}
                        stack.append(Q(**q_param))

                elif token in self.boolean_operators:
                    second_last_item.add(last_item, getattr(Q, token))
                    stack.append(second_last_item)

        return stack[0] if stack else Q()

    def parse_search_phrase(self) -> Q:
        """Uses phrase and allowed_fields to create Q object.

        The `phrase` and `allowed_fields` are defined during class initialization.

        :return: Q object constructed from user input
        """
        tokens = self.tokenize(self.phrase)

        postfix_tokens = self.to_postfix(tokens)

        filtered_postfix_tokens = self.filter_allowed_fields(
            allowed_fields=self.allowed_fields,
            tokens=postfix_tokens
        )

        q_object = self.postfix_to_q(filtered_postfix_tokens)

        return q_object
