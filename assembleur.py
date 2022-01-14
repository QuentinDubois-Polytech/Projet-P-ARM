import sys
import re
from pathlib import Path

if len(sys.argv) == 2:
    file_name_read = sys.argv[1]  # path of the file
    file_name_write = Path(sys.argv[1]).stem + ".bin"  # name of the entry file with the extension .bin
else:
    print("Il faut rentrer un fichier en paramètre")
    sys.exit()

line_counter = 0
line_instruction_main = 0


def line_analyser(assembly_language_instruction):
    """ Analyse an instruction of assembly language and redirect it into the right function"""
    list_instruction = list_conversion(assembly_language_instruction)
    if len(list_instruction) == 2:
        if assembly_language_instruction[0] == 'b' and list_instruction[0] != "bics":
            if assembly_language_instruction[1].isspace():
                label = assembly_language_instruction.split('.')[1]
                previous_line = file_read.tell()
                immediate11 = find_immediate_branch(label)
                unconditional_branch(immediate11)
                file_read.seek(previous_line)
            else:
                condition = assembly_language_instruction[1:3].upper()
                label = assembly_language_instruction.split('.')[1]
                previous_line = file_read.tell()
                immediate8 = find_immediate_branch(label)
                conditional_branch(conditional_branch_codop(condition), immediate8)
                file_read.seek(previous_line)

        else:
            instruction = list_instruction[0]
            list_parameters = parameters_analyser("".join(list_instruction[1:]).replace("r", ""))
            operation(instruction, assembly_language_instruction, list_parameters)


def operation(instruction, assembly_language_instruction, list_parameters):
    match instruction:
        case "lsls":
            shift("0100000010", "00000", assembly_language_instruction, list_parameters)

        case "lsrs":
            shift("0100000011", "00001", assembly_language_instruction, list_parameters)

        case "asrs":
            shift("0100000100", "00010", assembly_language_instruction, list_parameters)

        case "adds":
            adds_subs("0001100", "0001110", "00110", assembly_language_instruction, list_parameters)

        case "subs":
            adds_subs("0001101", "0001111", "00111", assembly_language_instruction, list_parameters)

        case "movs":
            op_immediate8("00100", assembly_language_instruction, list_parameters, False)

        case "ands":
            op_register_data_processing("0100000000", list_parameters)

        case "eors":
            op_register_data_processing("0100000001", list_parameters)

        case "adcs":
            op_register_data_processing("0100000101", list_parameters)

        case "sbcs":
            op_register_data_processing("0100000110", list_parameters)

        case "rors":
            op_register_data_processing("0100000111", list_parameters)

        case "tst":
            op_register_data_processing("0100001000", list_parameters)

        case "rsbs":
            op_register_data_processing("0100001001", list_parameters)

        case "cmp":
            cmp("0100001010", "00101", assembly_language_instruction, list_parameters)

        case "cmn":
            op_register_data_processing("0100001011", list_parameters)

        case "orrs":
            op_register_data_processing("0100001100", list_parameters)

        case "muls":
            op_register_data_processing("0100001101", list_parameters)

        case "bics":
            op_register_data_processing("0100001110", list_parameters)

        case "mvns":
            op_register_data_processing("0100001111", list_parameters)

        case "str":
            list_parameters = remover_sp_str_load(list_parameters)
            op_immediate8("10010", assembly_language_instruction, list_parameters, True)

        case "ldr":
            list_parameters = remover_sp_str_load(list_parameters)
            op_immediate8("10011", assembly_language_instruction, list_parameters, True)

        case "add":
            add_sub("101100000", list_parameters, assembly_language_instruction)

        case "sub":
            add_sub("101100001", list_parameters, assembly_language_instruction)


def conditional_branch_codop(string_condition):
    match string_condition:
        case "EQ":
            return "0000"

        case "NE":
            return "0001"

        case "CS":
            return "0010"

        case "HS":
            return "0010"

        case "CC":
            return "0011"

        case "LO":
            return "0011"

        case "MI":
            return "0100"

        case "PL":
            return "0101"

        case "VS":
            return "0110"

        case "VC":
            return "0111"

        case "HI":
            return "1000"

        case "LS":
            return "1001"

        case "GE":
            return "1010"

        case "LT":
            return "1011"

        case "GT":
            return "1100"

        case "LE":
            return "1101"

        case "AL":
            return "1111"


def cmp(codop_register, codop_immediate8, assembly_language_instruction, list_parameters):
    length = len(list_parameters)
    list_assembly_language_instruction = list_conversion(assembly_language_instruction)
    if "#" in list_assembly_language_instruction[1] and length == 2:
        op_immediate8(codop_immediate8, list_assembly_language_instruction[1], list_parameters, False)
    elif length == 2:
        op_register_data_processing(codop_register, list_parameters)
    else:
        instruction_error(list_assembly_language_instruction[0])


def shift(codop_register, codop_immediate5, assembly_language_instruction, list_parameters):
    """ Redirect the instruction of type shift into the right function """
    length = len(list_parameters)
    list_assembly_language_instruction = list_conversion(assembly_language_instruction)
    if "#" in list_assembly_language_instruction[1] and length == 3:
        op_immediate(codop_immediate5, 5, list_parameters)
    elif length == 2:
        op_register_data_processing(codop_register, list_parameters)
    else:
        instruction_error(list_assembly_language_instruction[0])


def adds_subs(codop_register, codop_immediate3, codop_immediate8, assembly_language_instruction, list_parameters):
    """ Redirect the instruction of type adds_subs into the right function """
    length = len(list_parameters)
    list_assembly_language_instruction = list_conversion(assembly_language_instruction)
    if "#" in list_assembly_language_instruction[1] and length == 3:
        op_immediate(codop_immediate3, 3, list_parameters)
    elif "#" in list_assembly_language_instruction[1] and length == 2:
        op_immediate8(codop_immediate8, list_assembly_language_instruction[1], list_parameters, False)
    elif length == 3:
        op_immediate(codop_register, 3, list_parameters)
    else:
        instruction_error(list_assembly_language_instruction[0])


def add_sub(codop, list_parameters, assembly_language_instruction):
    """ Calculate the conversion of the instruction of type add_sub in binary code
        And write the result in the file_name_write """
    list_assembly_language_instruction = list_conversion(assembly_language_instruction)
    if "sp" not in list_assembly_language_instruction[1] or "#" not in list_assembly_language_instruction[1]:
        instruction_error(list_assembly_language_instruction[0])
    elif len(list_parameters) != 2:
        instruction_error(list_assembly_language_instruction[0])
    else:
        list_parameters = remover_sp_add_sub(list_parameters)
        nb_immediate = 7
        immediate7 = immediate_divide_by_n(list_parameters[0], nb_immediate, 4)

        binary_code = convert_hex(codop + immediate7)
        print_file(binary_code)


def op_immediate(codop, nb_immediate, list_parameters):
    """ Calculate the conversion of the instruction of type op_immediate in binary code
        And write the result in the file_name_write """
    Rd = convert_binary(list_parameters[0], 3)
    Rm = convert_binary(list_parameters[1], 3)
    immediate5 = immediate(list_parameters[2], nb_immediate)

    binary_code = convert_hex(codop + immediate5 + Rm + Rd)
    print_file(binary_code)


def op_register_data_processing(codop, list_parameters):
    """ Calculate the conversion of the instruction of type op_register_data_processing in binary code
        And write the result in the file_name_write """
    Rdn = convert_binary(list_parameters[0], 3)
    Rm = convert_binary(list_parameters[1], 3)

    binary_code = convert_hex(codop + Rm + Rdn)
    print_file(binary_code)


def op_immediate8(codop, assembly_language_instruction, list_parameters, divide_by_4):
    """ Calculate the conversion of the instruction in binary code
        And write the result in the file_name_write """
    list_assembly_language_instruction = list_conversion(assembly_language_instruction)

    if len(list_parameters) != 2:
        instruction_error(list_assembly_language_instruction[0])
    elif "#" not in list_parameters[1]:
        instruction_error(list_assembly_language_instruction[0])
    else:
        Rd = convert_binary(list_parameters[0], 3)

        if divide_by_4:
            immediate8 = immediate_divide_by_n(list_parameters[1], 8, 4)
        else:
            immediate8 = immediate(list_parameters[1], 8)

        binary_code = convert_hex(codop + Rd + immediate8)
        print_file(binary_code)


def conditional_branch(condition, imm8):
    code = "1101" + condition + immediate(imm8, 8)
    binary_code = convert_hex(code)
    print_file(binary_code)


def unconditional_branch(imm11):
    code = "11100" + immediate(imm11, 11)
    binary_code = convert_hex(code)
    print_file(binary_code)


def find_immediate_branch(label):
    previous_line = line_instruction_main
    next_line = read_file_search_label(label)
    return str(next_line - previous_line - 3)


def list_conversion(assembly_language_instruction):
    return re.split("\s", assembly_language_instruction, 1)


def parameters_analyser(string_instruction):
    """ Return a list with the parameters of the instruction.
        A post treatment may be required for some instruction """
    return string_instruction.split(', ')


def instruction_error(string_instruction):
    """ Return an error with the name instruction and the line """
    print("erreur instruction " + string_instruction.upper() + " ligne : " + str(line_counter))


def remover_sp_str_load(list_parameters):
    """ Remove the sp and the brackets of the elements of the list """
    i = 0
    length = len(list_parameters)
    while i < length:
        list_parameters[i] = list_parameters[i].replace("[", "").replace("]", "").replace("sp", "")
        i += 1
    list_parameters.remove("")

    if len(list_parameters) == 1:
        list_parameters.append("#0")
    return [list_parameters[0], list_parameters[1]]


def remover_sp_add_sub(list_parameters):
    """ Remove "sp" of the elements of the list """
    return [list_parameters[1]]


def immediate_divide_by_n(string_immediate, nb_immediate, n):
    """ Convert the string representing an immediate in a string representing the number divided by n without the '#'
        and with the same number of digits indicated by the parameter nb_immediate"""
    return "{0:b}".format(int(string_immediate.strip('#'), 10) // n).zfill(nb_immediate)


def immediate(string_immediate, nb_immediate):
    """ Convert the string representing an immediate in a string representing the same number without the '#'
        and with the same number of digits indicated by the parameter nb_immediate"""

    string_decimal = string_immediate.lstrip('#')
    return convert_binary(string_decimal, nb_immediate)


def convert_hex(string_number):
    """ Convert a string representing a number in base 2 in a string representing the same number in the base 16 """
    return "{0:x}".format(int(string_number, 2)).zfill(4)


# Returns bit y of x (10 base).  i.e.
# bit 2 of 5 is 1
# bit 1 of 5 is 0
# bit 0 of 5 is 1
# Code provenant : https://askcodez.com/en-complement-a-deux-binaires-en-python.html
def get_bit(y, x):
    return str((x >> y) & 1)


# Returns the first `count` bits of base 10 integer `x`
# Code provenant : https://askcodez.com/en-complement-a-deux-binaires-en-python.html
def convert_binary(x, count=8):
    x = int(x, 10)
    shift = range(count - 1, -1, -1)
    bits = map(lambda y: get_bit(y, x), shift)
    return "".join(bits)


def erase_file(file_name):
    """ Erase all the content of the file passed in parameter"""
    with open(file_name, 'w'):
        pass


def print_file(string_hexa_code):
    """ Write the string passed in parameter in the file"""
    print(string_hexa_code)
    file_write.write(string_hexa_code + " ")


def read_file():
    """ Read each line of the file passed in parameter"""
    global line_counter
    global line_instruction_main

    while file_line := file_read.readline().strip():
        line_counter += 1

        if file_read is None:
            break
        if not file_line.startswith('.') and not file_line.startswith(
                '@') and file_line != '\n':  # to skip the comments and empty line
            line_instruction_main += 1
            line_analyser(file_line.strip())

def read_file_search_label(label):
    line_instruction_secondary = 0
    file_read.seek(0)

    while file_line := file_read.readline().strip():
        if not file_line.startswith('.') and not file_line.startswith('@') and file_line != '\n':
            line_instruction_secondary += 1
        if file_line == "." + label + ":":  # to skip the comments and empty line
            return line_instruction_secondary + 1


if __name__ == '__main__':
    erase_file(file_name_write)
    file_read = open(file_name_read, 'r')
    file_write = open(file_name_write, 'a')
    read_file()
    file_read.close()
    file_write.close()
