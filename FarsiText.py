import bpy
import os

# general: (Isolated, Final, Initial)
farsi_chars = {
    'ا': (0xFE8D, True, False),
    'أ': (0xFE83, True, False),
    'إ': (0xFE87, True, False),
    'آ': (0xFE81, True, False),
    'ء': (0xFE80, False, False),
    'ب': (0xFE8F, True, True),
    'پ': (0xFB56, True, True),
    'ت': (0xFE95, True, True),
    'ث': (0xFE99, True, True),
    'ج': (0xFE9D, True, True),
    'چ': (0xFB7A, True, True),
    'ح': (0xFEA1, True, True),
    'خ': (0xFEA5, True, True),
    'د': (0xFEA9, True, False),
    'ذ': (0xFEAB, True, False),
    'ر': (0xFEAD, True, False),
    'ز': (0xFEAF, True, False),
    'ژ': (0xFB8A, True, False),
    'س': (0xFEB1, True, True),
    'ش': (0xFEB5, True, True),
    'ص': (0xFEB9, True, True),
    'ض': (0xFEBD, True, True),
    'ط': (0xFEC1, True, True),
    'ظ': (0xFEC5, True, True),
    'ع': (0xFEC9, True, True),
    'غ': (0xFECD, True, True),
    'ف': (0xFED1, True, True),
    'ق': (0xFED5, True, True),
    'ك': (0xFED9, True, True),
    'ک': (0xFB8E, True, True),
    'گ': (0xFB92, True, True),
    'ل': (0xFEDD, True, True),
    'م': (0xFEE1, True, True),
    'ن': (0xFEE5, True, True),
    'ه': (0xFEE9, True, True),
    'ة': (0xFE93, True, False),
    'و': (0xFEED, True, False),
    'ؤ': (0xFE85, True, False),
    'ي': (0xFEF1, True, True),
    'ی': (0xFEEF, True, True),
    'ئ': (0xFE89, True, True),
}

combinations = {
    'لا': 0xFEFB,
    'لأ': 0xFEF7,
    'لإ': 0xFEF9,
    'لآ': 0xFEF5,
}

def find_combination(current_char: str, next_char: str):
    for combination, char_code in combinations.items():
        if combination[0] == current_char and combination[1] == next_char:
            return char_code
    return 0

chars_farsi_symbols = ['ـ', '،', '؟', '×', '÷']
chars_common = [' ', '.', ',', ':', '|', '(', ')', '[', ']', '{', '}', '!', '+', '-', '*', '/', '\\', '%', '"', '\'', '>', '<', '=', '~', '_']
chars_digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# Check if a letter should be connected to the letter preceding it
def can_be_final(c):
    if c not in farsi_chars:
        return False
    return farsi_chars[c][1]


# Check if a letter should be connected to the letter next to it
def can_be_initial(c):
    if c not in farsi_chars:
        return False
    return farsi_chars[c][2]

# Get the location (unicode id) of an Farsi letter shapes (when connected)
def get_char_variants_base(c):
    if c not in farsi_chars:   # It's not an Farsi char
        return -1
    return farsi_chars[c][0]

#
def is_farsi_char(c):
    if c == 'ـ': # Low line
        return True
    if c in farsi_chars:
        return True
    return False


# Farsi char variants are located at 0xFE70 to  0xFEFE on unicode fonts.
def is_farsi_char_variant(c):
    if ord(c) >= 0xFE70 and ord(c) <= 0xFEFE:
        return True
    return False


# Get the previous character from a buffer or text array
def get_previous_alphabet(index, text):
    index -= 1
    while index > 0 and (text[index] in chars_common or text[index] in chars_digits or text[index] in chars_farsi_symbols):
        index -= 1
    if index >= 0:
        return text[index]
    else:
        return None

# Get the next character from a buffer or text array
def get_next_alphabet(index, text):
    index += 1
    while index < len(text) and (text[index] in chars_common or text[index] in chars_digits or text[index] in chars_farsi_symbols):
        index += 1

    if index < len(text):
        return text[index]
    else:
        return None

# Link Farsi letters
def link_text(unlinked_text):
    linked_text = []
    previous_char = ""
    next_char = ""
    char_code = 0
    skip_char = False

    # When the letter "Alef" is connected to the letter "Lem" they become one letter
    # but the buffer still contains the two
    uncounted_chars = 0

    for current_char in unlinked_text:
        
        if skip_char:
            skip_char = False
            continue

        chars_count = len(linked_text) + uncounted_chars

        previous_char = unlinked_text[chars_count - 1] if chars_count > 0 else ""
        next_char = unlinked_text[chars_count + 1] if chars_count < len(unlinked_text) - 1 else ""

        char_code = find_combination(current_char, next_char)
        if char_code != 0:
            if can_be_initial(previous_char):
                char_code += 1
            linked_text.insert(0, chr(char_code))
            uncounted_chars += 1
            skip_char = True
            continue

        if current_char in chars_farsi_symbols:
            linked_text.insert(0, current_char)
            continue

        if current_char == '\n':
            linked_text.insert(0, current_char)
            continue

        # Common characters follows the direction of the previous text (RTL or LTR)
        if current_char in chars_common:
            
            previous_alpha = get_previous_alphabet(chars_count, unlinked_text)
            next_alpha = get_next_alphabet(chars_count, unlinked_text)
            
            char_pos = 0

            if not is_farsi_char(previous_alpha) and not is_farsi_char(next_alpha) and previous_alpha != '\n':
                
                while char_pos < len(linked_text) and not is_farsi_char_variant(linked_text[char_pos]) and linked_text[char_pos] != '\n':
                    char_pos += 1
            
            linked_text.insert(char_pos, current_char)

            continue

        # Other letters

        char_code = get_char_variants_base(current_char)
        
        if char_code == -1:   # = Not an Farsi character

            # Do not reverse non-Farsi characters

            previous_alpha = get_previous_alphabet(chars_count, unlinked_text)
            next_alpha = get_next_alphabet(chars_count, unlinked_text)

            char_pos = 0

            # Numbers

            if len(linked_text) > 0 and linked_text[0] in chars_digits:
                while char_pos < len(linked_text) and linked_text[char_pos] in chars_digits:
                    char_pos +=1
            
            # Non-Farsi alhpabet

            elif not is_farsi_char(previous_alpha):
                c = chars_count - 1
                while not is_farsi_char(previous_alpha) and char_pos < len(linked_text) and linked_text[char_pos] != '\n':
                    previous_alpha = get_previous_alphabet(c, unlinked_text)
                    char_pos += 1
                    c -= 1

            linked_text.insert(char_pos, current_char)

            continue

        # It's an Farsi alhpabet

        if can_be_initial(previous_char) and can_be_final(current_char):

            if can_be_initial(current_char) and can_be_final(next_char):
                
                if char_code == 65263: # ی
                    char_code += 5
                else:
                    char_code += 3

            else:

                char_code += 1
        else:

            if can_be_initial(current_char) and can_be_final(next_char):
                
                if char_code == 65263:
                    char_code += 4
                else:
                    char_code += 2
            else:
                char_code = ord(current_char)

        linked_text.insert(0, chr(char_code))

    text = ''.join(linked_text)

    return text


# swap lines

# When we reverse the order of our characters (to show farsi text correctly), we will get our lines of text swaped
# so we have to swap our text lines back to make it shown correctly
def swap_lines(linked_text):

    new_text = []
    current_line_start = 0
    char_counter = 0

    for c in reversed(linked_text):
        if c == '\n':
            new_text.append('\n')
            current_line_start = char_counter + 1
            char_counter += 1
            continue

        new_text.insert(current_line_start, c)
        char_counter += 1

    return ''.join(new_text)


# Unlink farsi text (get the original text before it gets connected)
def unlink_text(linked_text):
    unlinked_text = []

    for c in linked_text:

        if ord(c) in {0xFE8D, 0xFE8E}:
            unlinked_text.insert(0, 'ا')

        elif ord(c) in {0xFE83, 0xFE84}:
            unlinked_text.insert(0, 'أ')

        elif ord(c) in {0xFE87, 0xFE88}:
            unlinked_text.insert(0, 'إ')

        elif ord(c) in {0xFE81, 0xFE82}:
            unlinked_text.insert(0, 'آ')

        elif ord(c) in {0xFE80}:
            unlinked_text.insert(0, 'ء')

        elif ord(c) in {0xFE8F, 0xFE90, 0xFE91, 0xFE92}:
            unlinked_text.insert(0, 'ب')
        
        elif ord(c) in {0xFB56, 0xFB57, 0xFB58, 0xFB59}:
            unlinked_text.insert(0, 'پ')

        elif ord(c) in {0xFE95, 0xFE96, 0xFE97, 0xFE98}:
            unlinked_text.insert(0, 'ت')

        elif ord(c) in {0xFE99, 0xFE9A, 0xFE9B, 0xFE9C}:
            unlinked_text.insert(0, 'ث')

        elif ord(c) in {0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0}:
            unlinked_text.insert(0, 'ج')
        
        elif ord(c) in {0xFB7A, 0xFB7B, 0xFB7C, 0xFB7D}:
            unlinked_text.insert(0, 'چ')

        elif ord(c) in {0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4}:
            unlinked_text.insert(0, 'ح')

        elif ord(c) in {0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8}:
            unlinked_text.insert(0, 'خ')

        elif ord(c) in {0xFEA9, 0xFEAA}:
            unlinked_text.insert(0, 'د')

        elif ord(c) in {0xFEAB, 0xFEAC}:
            unlinked_text.insert(0, 'ذ')

        elif ord(c) in {0xFEAD, 0xFEAE}:
            unlinked_text.insert(0, 'ر')

        elif ord(c) in {0xFEAF, 0xFEB0}:
            unlinked_text.insert(0, 'ز')

        elif ord(c) in {0xFB8A, 0xFB8B}:
            unlinked_text.insert(0, 'ژ')

        elif ord(c) in {0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4}:
            unlinked_text.insert(0, 'س')

        elif ord(c) in {0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8}:
            unlinked_text.insert(0, 'ش')

        elif ord(c) in {0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC}:
            unlinked_text.insert(0, 'ص')

        elif ord(c) in {0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0}:
            unlinked_text.insert(0, 'ض')

        elif ord(c) in {0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4}:
            unlinked_text.insert(0, 'ط')

        elif ord(c) in {0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8}:
            unlinked_text.insert(0, 'ظ')

        elif ord(c) in {0xFEC9, 0xFECA, 0xFECB, 0xFECC}:
            unlinked_text.insert(0, 'ع')

        elif ord(c) in {0xFECD, 0xFECE, 0xFECF, 0xFED0}:
            unlinked_text.insert(0, 'غ')

        elif ord(c) in {0xFED1, 0xFED2, 0xFED3, 0xFED4}:
            unlinked_text.insert(0, 'ف')

        elif ord(c) in {0xFED5, 0xFED6, 0xFED7, 0xFED8}:
            unlinked_text.insert(0, 'ق')

        elif ord(c) in {0xFED9, 0xFEDA, 0xFEDB, 0xFEDC}:
            unlinked_text.insert(0, 'ك')

        elif ord(c) in {0xFB8E, 0xFB8F, 0xFB90, 0xFB91}:
            unlinked_text.insert(0, 'ﮎ')

        elif ord(c) in {0xFB92, 0xFB93, 0xFB94, 0xFB95}:
            unlinked_text.insert(0, 'گ')

        elif ord(c) in {0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0}:
            unlinked_text.insert(0, 'ل')

        elif ord(c) in {0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4}:
            unlinked_text.insert(0, 'م')

        elif ord(c) in {0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8}:
            unlinked_text.insert(0, 'ن')

        elif ord(c) in {0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC}:
            unlinked_text.insert(0, 'ه')

        elif ord(c) in {0xFE93, 0xFE94}:
            unlinked_text.insert(0, 'ة')

        elif ord(c) in {0xFEED, 0xFEEE}:
            unlinked_text.insert(0, 'و')

        elif ord(c) in {0xFE85, 0xFE86}:
            unlinked_text.insert(0, 'ؤ')

        elif ord(c) in {0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4}:
            unlinked_text.insert(0, 'ي')

        elif ord(c) in {0xFEEF, 0xFEF0}:
            unlinked_text.insert(0, 'ی')

        elif ord(c) in {0xFE89, 0xFE8A, 0xFE8B, 0xFE8C}:
            unlinked_text.insert(0, 'ئ')

        elif ord(c) in {0xFEFB, 0xFEFC}:
            unlinked_text.insert(0, 'ا')
            unlinked_text.insert(0, 'ل')

        elif ord(c) in {0xFEF7, 0xFEF8}:
            unlinked_text.insert(0, 'أ')
            unlinked_text.insert(0, 'ل')

        elif ord(c) in {0xFEF9, 0xFEFA}:
            unlinked_text.insert(0, 'إ')
            unlinked_text.insert(0, 'ل')

        elif ord(c) in {0xFEF5, 0xFEF6}:
            unlinked_text.insert(0, 'آ')
            unlinked_text.insert(0, 'ل')

        # Other characters
        else:
            unlinked_text.insert(0, c)

    return unlinked_text


# Prepare our text (3D text, text_buffer)

class Text:
    text_buffer = []
    current_char_index = 0
    
    def __init__(self, src: str):
        self.text_buffer = unlink_text(swap_lines(src))
        self.current_char_index = len(src)
        self.update_visual_cursor_position()

    def update_text(self):
        
        linked_text = link_text(self.text_buffer)
        linked_text = swap_lines(linked_text)
        
        bpy.ops.font.select_all()
        bpy.ops.font.delete()
        bpy.ops.font.text_insert(text=linked_text)
        
        self.update_visual_cursor_position()

    # Add a new character
    def insert_char(self, char):
        self.text_buffer.insert(self.current_char_index, char)
        self.current_char_index += 1
        self.update_text()
        

    # Add a new character
    def insert_text(self, text):
        self.text_buffer[self.current_char_index : self.current_char_index] = list(text)
        self.current_char_index += len(text)
        self.update_text()

    # Move the cursor (well, our pointer) to the previous char/position
    def move_previous(self):
        if self.current_char_index > 0:
            self.current_char_index -= 1
        
        self.update_visual_cursor_position()


    # Move the cursor/pointer to the next char/position
    def move_next(self):
        if self.current_char_index < len(self.text_buffer):
            self.current_char_index += 1
            
        self.update_visual_cursor_position()


    # Move the cursor/pointer to the start of the current line
    def move_line_start(self):
        while self.current_char_index > 0:
            self.current_char_index -= 1
            if self.text_buffer[self.current_char_index] == '\n':
                self.current_char_index += 1
                break
            
        self.update_visual_cursor_position()


    # Move the cursor/pointer to the end of the current line
    def move_line_end(self):
        while self.current_char_index < len(self.text_buffer):
            if self.text_buffer[self.current_char_index] == '\n':
                break
            self.current_char_index += 1
            
        self.update_visual_cursor_position()


    # Move the cursor/pointer to the previous line
    def move_up(self):
        line_start = self.get_line_start()
        line_offset = self.current_char_index - line_start
        previous_line_end = line_start - 2
        previous_line_start = self.get_line_start(previous_line_end)
        previous_line_size = previous_line_end - previous_line_start
        new_index = previous_line_start + min(line_offset, previous_line_size + 1)
        
        if self.is_valid_char_index(new_index):
            self.current_char_index = new_index
            self.update_visual_cursor_position()


    # Move the cursor/pointer to the next line
    def move_down(self):
        
        new_line_size = 0
        
        line_start = self.get_line_start()
        line_offset = self.current_char_index - line_start
        
        new_index = self.get_next_line_start()
        
        if new_index == -1:
            return
        
        for i in range(line_offset):
            
            if not self.is_valid_char_index(new_index):
                break
            
            if self.text_buffer[new_index] == '\n':
                break
            
            new_index += 1
            
        if self.is_valid_char_index(new_index) or new_index == len(self.text_buffer):
            self.current_char_index = new_index
            self.update_visual_cursor_position()


    # Delete the previous character
    def delete_previous(self):
        if self.current_char_index > 0:
            self.text_buffer.pop(self.current_char_index - 1)
            self.current_char_index -= 1
            self.update_text()


    # Delete the next character
    def delete_next(self):
        if self.is_valid_char_index(self.current_char_index):
            del self.text_buffer[self.current_char_index]
            
            self.update_text()


    #

    def get_line_start(self, index=-1):
        line_start = self.current_char_index if index == - 1 else index
        while line_start > 0:
            line_start -= 1
            if self.text_buffer[line_start] == '\n':
                line_start += 1
                break
            
        return line_start


    #

    def get_next_line_start(self):
        next_line_start = self.current_char_index
        while next_line_start < len(self.text_buffer):
            if self.text_buffer[next_line_start] == '\n':
                next_line_start += 1
                break
            
            next_line_start += 1
            if next_line_start == len(self.text_buffer):
                return -1
            
        return next_line_start

    def is_valid_char_index(self, index):
        if len(self.text_buffer) > 0 and index >= 0 and index < len(self.text_buffer):
            return True
        return False


    # Make the visual cursor follow our pointer
    def update_visual_cursor_position(self):
        # Move visual cursor to the begining of the text
        for i in range(len(self.text_buffer)):
            bpy.ops.font.move(type='PREVIOUS_CHARACTER')
        
        current_line_start = self.get_line_start()
        for i in range(current_line_start):
            if self.text_buffer[i] == '\n':
                bpy.ops.font.move(type='NEXT_LINE')
        
        # NOTE: we can do this in another way, without moving the cursor to the and of the line and then bring it back
        # we can just count the length of the current line and move the cursor forward:
        # (line_length - current_line_offset(= self.current_char_index - line_start)) times
        
        bpy.ops.font.move(type='LINE_END')
        
        for i in range(current_line_start, self.current_char_index):
            
            # Do not count "Lem-Alef" as two letters
            if self.text_buffer[i] in {'ا', 'أ', 'إ', 'آ'}:
                if i > 0 and self.text_buffer[i - 1] == 'ل':
                    continue
                
            bpy.ops.font.move(type='PREVIOUS_CHARACTER')

