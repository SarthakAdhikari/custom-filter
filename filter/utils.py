import re

from django.db.models import Q

class CustomFilter:
    tokenizer_regex = r"([0-9]{4}-[0-9]{1,2}-[0-9]{1,2}|\b\w*[\.]?\w+\b|[\(\)])"
    word_operators = ["eq", "ne", "lt", "gt", "AND", "OR"]
    all_operators = word_operators + ["(", ")"]
    boolean_operators = ["AND", "OR", "NOT"]
    precedence = {
        "eq": 2,
        "ne": 3,
        "lt": 3,
        "gt": 3,
        "AND": 2,
        "OR": 1,
    }

    def __init__(self, allowed_fields, phrase):
        self.allowed_fields = allowed_fields
        self.phrase = phrase

    def tokenize(self, source):
        return re.findall(self.tokenizer_regex, source)

    def to_postfix(self, tokens):
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

    def filter_allowed_fields(self, allowed_fields, tokens):
        token_index_to_remove = set()

        for index, token in enumerate(tokens):
            # is token a value like `2020-01-01`?
            is_value = index % 3 == 1

            if token in self.word_operators:
                continue

            if token not in self.allowed_fields and not is_value:
                token_index_to_remove.update([index, index+1, index+2])

        tokens = [val for ind, val in enumerate(tokens)
                  if ind not in token_index_to_remove]

        return tokens

    def postfix_to_q(self, tokens):
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
                    if token == "ne":
                        q_param = {second_last_item: last_item}
                        stack.append(~Q(**q_param))
                    else:
                        q_query_string = second_last_item + "__" + token
                        q_param = {q_query_string: last_item}
                        stack.append(Q(**q_param))

                elif token in self.boolean_operators:
                    second_last_item.add(last_item, getattr(Q, token))
                    stack.append(second_last_item)

        return stack[0] if stack else Q()

    def parse_search_phrase(self):
        tokens = self.tokenize(self.phrase)

        postfix_tokens = self.to_postfix(tokens)

        filtered_postfix_tokens = self.filter_allowed_fields(
            allowed_fields=self.allowed_fields,
            tokens=postfix_tokens
        )

        q_object = self.postfix_to_q(filtered_postfix_tokens)

        return q_object
