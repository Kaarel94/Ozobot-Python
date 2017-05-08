class ColorLanguageTranslator:
    START = "CRYCYMCRW"
    END = "CMW"

    @staticmethod
    def base7(num):
        if num == 0:
            return '0'

        new_num_string = ''
        current = num
        while current != 0:
            remainder = current % 7
            remainder_string = str(remainder)
            new_num_string = remainder_string + new_num_string
            current //= 7
        return new_num_string

    # Function for converting a base-7 number(given as a string) to a 3 digit color code:
    @staticmethod
    def base7_to_color_code(num):
        colorDict = {
            '0': 'K',
            '1': 'R',
            '2': 'G',
            '3': 'Y',
            '4': 'B',
            '5': 'M',
            '6': 'C',
        }

        if len(num) == 1:
            num = "00" + num
        elif len(num) == 2:
            num = "0" + num

        chars = list(num)

        return colorDict[chars[0]] + colorDict[chars[1]] + colorDict[chars[2]]

    @staticmethod
    def translate(byte_array):
        color_sequence = "".join([ColorLanguageTranslator.base7_to_color_code(ColorLanguageTranslator.base7(x)) for x in byte_array])

        sequence_with_repetition = ColorLanguageTranslator.START + color_sequence + ColorLanguageTranslator.END

        end_sequence = ""
        for i, c in enumerate(sequence_with_repetition):
            if i == 0 or sequence_with_repetition[i - 1] != c or end_sequence[i - 1] == 'W':
                end_sequence += c
            else:
                end_sequence += 'W'

        return end_sequence