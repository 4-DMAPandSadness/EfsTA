from PyQt5.QtGui import QValidator
import re

class EquationValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, string, pos):
        pattern = re.compile(r'^([A-Zv])*; | ([A-Zv]?-?>?)*[A-Zv]?;$')
        inv = ["--", ";;", ">>", ";>", ";-", ">-", ">;", "-;"]
        if pattern.match(string):
            return QValidator.Acceptable, string, pos
        if re.match(r'^(([A-Zv]?-?>?[A-Zv]?)*;?)*$', string):
            for i in inv:
                if i in string:
                    return QValidator.Invalid, string, pos
            return QValidator.Intermediate, string, pos
        return QValidator.Invalid, string, pos
    
    def fixup(self, input):
        pass

class EmptyListValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, string, pos):
        pattern = re.compile(r'^(\d*\.\d*,)*\d*\.\d*$')
        if pattern.match(string):
            return QValidator.Acceptable, string, pos
        if re.match(r'\d*\.?\d*,?', string):
            if ",.," in string:
                return QValidator.Invalid, string, pos
            parts = string.split(',')
            for part in parts:
                if part.count('.') > 1:
                    return QValidator.Invalid, string, pos
            return QValidator.Intermediate, string, pos
        return QValidator.Invalid, string, pos

    def fixup(self, input):
        pass
    
class ListValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, string, pos):
        pattern = re.compile(r'^(\d*\.\d*,)*\d*\.\d*$')
        if pattern.match(string):
            return QValidator.Acceptable, string, pos
        if re.match(r'\d*\.?\d*,?', string):
            if ",," in string or ",.," in string:
                return QValidator.Invalid, string, pos
            parts = string.split(',')
            for part in parts:
                if part.count('.') > 1:
                    return QValidator.Invalid, string, pos
            return QValidator.Intermediate, string, pos
        return QValidator.Invalid, string, pos

    def fixup(self, input):
        pass

class ValueValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, string, pos):
        pattern = re.compile(r'^\d*\.\d*$')
        if pattern.match(string):
            return QValidator.Acceptable, string, pos
        if re.match(r'^\d*\.?\d*$', string):
            if string.count('.') <= 1:
                return QValidator.Intermediate, string, pos
        return QValidator.Invalid, string, pos

    def fixup(self, input):
        pass
