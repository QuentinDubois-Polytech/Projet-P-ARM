import sys
from pathlib import Path

file_name_read = sys.argv[1]  # path of the file
file_name_write = Path(sys.argv[1]).stem + ".bin"  # name of the entry file with the extension .bin
line_counter = 0


def line_analyser(assembly_language_instruction):
    """ Analyse an instruction of assembly language and redirect it into the right function"""
    list_instruction = assembly_language_instruction.split(' ', 1)

    if len(list_instruction) <= 1:
        raise ValueError("Instruction incorrect : ligne " + str(line_counter))

    instruction = list_instruction[0]
    string_instruction = "".join(list_instruction)
    list_parameters = parameters_analyser("".join(list_instruction[1:]).replace("r", ""))

    match instruction:
        case "lsls":
            shift("0100000010", "00000", string_instruction, list_parameters)

        case "lsrs":
            shift("0100000011", "00001", string_instruction, list_parameters)

        case "asrs":
            shift("0100000100", "00010", string_instruction, list_parameters)

        case "adds":
            adds_subs("0001100", "0001110", "00110", string_instruction, list_parameters)

        case "subs":
            adds_subs("0001101", "0001111", "00111", string_instruction, list_parameters)

        case "movs":
            op_immediate8("00100", string_instruction, list_parameters, False)

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
            shift("0100001010", "00101", string_instruction, list_parameters)

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
            op_immediate8("10010", string_instruction, list_parameters, True)

        case "ldr":
            list_parameters = remover_sp_str_load(list_parameters)
            op_immediate8("10011", string_instruction, list_parameters, True)

        case "add":
            list_parameters = remover_sp_add_sub(list_parameters)
            add_sub("101100000", list_parameters, string_instruction)

        case "sub":
            list_parameters = remover_sp_add_sub(list_parameters)
            add_sub("101100001", list_parameters, string_instruction)


def shift(codop_register, codop_immediate5, string_parameters, list_parameters):
    """ Redirect the instruction of type shift into the right function """
    length = len(list_parameters)
    if "#" in string_parameters and length == 3:
        op_immediate(codop_immediate5, 5, list_parameters)
    elif length == 2:
        op_register_data_processing(codop_register, list_parameters)
    else:
        instruction_error(string_parameters)


def adds_subs(codop_register, codop_immediate3, codop_immediate8, string_instruction, list_parameters):
    """ Redirect the instruction of type adds_subs into the right function """
    length = len(list_parameters)
    if "#" in string_instruction and length == 3:
        op_immediate(codop_immediate3, 3, list_parameters)
    elif "#" in string_instruction and length == 2:
        op_immediate8(codop_immediate8, string_instruction, list_parameters, False)
    elif length == 3:
        op_immediate(codop_register, 3, list_parameters)
    else:
        instruction_error(string_instruction)


def add_sub(codop, list_parameters, string_instruction):
    """ Calculate the conversion of the instruction of type add_sub in binary code
        And write the result in the file_name_write """
    if "sp" not in string_instruction or "#" not in string_instruction:
        instruction_error(string_instruction)
    if len(list_parameters) != 1:
        instruction_error(string_instruction)

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


def op_immediate8(codop, string_instruction, list_parameters, divide_by_4):
    """ Calculate the conversion of the instruction in binary code
        And write the result in the file_name_write """
    if len(list_parameters) != 2:
        instruction_error(string_instruction)

    Rd = convert_binary(list_parameters[0], 3)

    if divide_by_4:
        immediate8 = immediate_divide_by_n(list_parameters[1], 8, 4)
    else:
        immediate8 = immediate(list_parameters[1], 8)

    binary_code = convert_hex(codop + Rd + immediate8)
    print_file(binary_code)


def parameters_analyser(string_instruction):
    """ Return a list with the parameters of the instruction.
        A post treatment may be required for some instruction """
    return string_instruction.split(', ')


def instruction_finder(string_instruction):
    """ Find the name of the instruction through a string containing the instruction """
    return string_instruction.split(' ')[0]


def instruction_error(string_instruction):
    """ Return an error with the name instruction and the line """
    raise ValueError("Erreur Instruction " + instruction_finder(string_instruction) + " ligne : " + str(line_counter))


def remover_sp_str_load(list_parameters):
    """ Remove the sp and the brackets of the elements of the list """
    return [list_parameters[0], list_parameters[2].replace("]", "")]


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
    return "{0:b}".format(int(string_immediate.strip('#'), 10)).zfill(nb_immediate)


def convert_hex(string_number):
    """ Convert a string representing a number in base 2 in a string representing the same number in the base 16 """
    return "{0:x}".format(int(string_number, 2)).zfill(4)


def convert_binary(string_number, nb_bytes):
    """ Convert a string representing a decimal number in a string representing the same number in the base 2 """
    return "{0:b}".format(int(string_number, 10)).zfill(nb_bytes)


def erase_file(file_name):
    """ Erase all the content of the file passed in parameter"""
    with open(file_name, 'w'):
        pass


def print_file(string):
    """ Write the string passed in parameter in the file"""
    print(string)
    with open(file_name_write, 'a') as file_write:
        file_write.write(string + " ")


def read_file(file_name):
    """ Read each line of the file passed in parameter"""
    global line_counter

    with open(file_name, 'r') as file_read:
        file_line = file_read.readline()

        while file_line:
            line_counter += 1
            if not file_line.startswith('@') and file_line != '\n':  # to skip the comments
                line_analyser(file_line)
            file_line = file_read.readline()


if __name__ == '__main__':
    erase_file(file_name_write)
    read_file(file_name_read)
