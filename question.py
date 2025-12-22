class Question:
    def __init__(self, text, options, answer):
        self.text = text
        self.options = options   # ["A. ...", "B. ..."]
        self.answer = answer     # "A", "B", "C", "D"

    def check_answer(self, user_answer_letter):
        return user_answer_letter.upper() == self.answer.upper()
