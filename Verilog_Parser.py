import re
import sys
import os

def file_reader(file_name):
    x = []
    try:
        # Open the file in read mode
        with open(file_name, 'r') as file:
            # Read and print each line
            for line in file:
                x.append(line.strip())  

    except FileNotFoundError:
        print(f"File not found: {file_name}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return x

statement_lists = []
file_path = 'tst.v'

verilog_code = file_reader(file_path)
    

def counting_modules(verilog_code):
    module_counter = 0
    for i in verilog_code:
        if i == "endmodule":
            module_counter += 1
    return module_counter

def creating_module_lists(verilog_code, module_lists, module_counter):
    for i in verilog_code:
        module_lists[len(module_lists)-module_counter].append(i)
        if i == "endmodule":
            module_counter -= 1
    return module_lists

def remove_empty_strings(module_lists):
    for i in module_lists:
     while("" in i) : 
        i.remove("")
    return module_lists

def remove_comments(module_lists):
    i_counter = 0
    for i in module_lists:
        
        j_counter = 0
        
        for j in i:
            
            if j.startswith('//'):
                i.remove(j)
            
            elif '//' in j:
                index = j.find('//')
                tmp = j[index:].split(" ")
                if "synopsys" in tmp:
                    break
                j = j[:index]
                module_lists[i_counter][j_counter] = j
            
            j_counter += 1

        i_counter += 1
    return module_lists

module_counter = counting_modules(verilog_code)
module_lists_space = [[] for i in range(module_counter)]
module_lists_space = creating_module_lists(verilog_code, module_lists_space, module_counter)
line_num_list = []

def creating_line_num_list(module_lists_space):
    tmp = 0
    for i in module_lists_space:
        for line_num,j in enumerate(i):
            x = line_num+tmp
            line_num_list.append([module_lists_space.index(i),x,j]) # module number , line number , line
        tmp = x+1
    return line_num_list

line_num_list = creating_line_num_list(module_lists_space)
module_lists = [[] for i in range(module_counter)]
# append each module to a module_lists from the y
module_lists = creating_module_lists(verilog_code, module_lists, module_counter)
# remove all empty strings from the module_lists
module_lists = remove_empty_strings(module_lists)
module_lists = remove_comments(module_lists)

def calculating_case_index(module_lists):
    cases_index = []
    for i in module_lists:
        for j in i:
            cmp = re.search("^case",j)
            if cmp or re.search("^casez",j) or re.search("^casex",j):
                cases_index.append(module_lists.index(i))
    return cases_index

def generating_reg_list(module_lists,any_specific_index):
    reg_list = []
    # in each list first number is case_index and second number is reg_index & size of reg is third number
    for i in any_specific_index:
        for j in module_lists[i]:
            if j.startswith('input'):
                j = j[len('input '):]
            if j.startswith('output'):
                j = j[len('output '):]
            if j.startswith('localparam'):
                j = j[len('localparam '):]
                if ']' in j or '[' in j:
                    low_bound = j.find('[')
                    high_bound = j.find(']')
                    size = j[low_bound+1:high_bound]
                    size = size.split(':')
                    size = int(size[0])-int(size[1])+1
                    j = j[high_bound+1:].replace(';', '')
                    j = j.replace(' ', '')
                    variables_names = j.split(',')
                    for var_name in variables_names:
                        reg_list.append([i, var_name, size])
                else:
                    size = 1
                    low_bound = j.find('g')
                    j = j[low_bound+1:].replace(';', '')
                    j = j.replace(' ', '')
                    variables_names = j.split(',')
                    for var_name in variables_names:
                        reg_list.append([i, var_name, size])  
                
            if j.startswith('reg'):
                # store reg name & size in a list
                if ']' in j or '[' in j:
                    low_bound = j.find('[')
                    high_bound = j.find(']')
                    size = j[low_bound+1:high_bound]
                    size = size.split(':')
                    size = int(size[0])-int(size[1])+1
                    j = j[high_bound+1:].replace(';', '')
                    j = j.replace(' ', '')
                    variables_names = j.split(',')
                    for var_name in variables_names:
                        reg_list.append([i, var_name, size])
                else:
                    size = 1
                    low_bound = j.find('g')
                    j = j[low_bound+1:].replace(';', '')
                    j = j.replace(' ', '')
                    variables_names = j.split(',')
                    for var_name in variables_names:
                        reg_list.append([i, var_name, size])  
    #print(reg_list)
    return reg_list

def check_full_case(module_lists):
    cases_index = calculating_case_index(module_lists)
    reg_list = generating_reg_list(module_lists,cases_index)
    size_list_for_case = []
    mask = 0
    for i in cases_index:
        for j in module_lists[i]:
            for t in reg_list:
                if t[0] == i and t[1] in j:
                    tmp = j.split("=")
                    if len(tmp) > 1:
                        #print(tmp)
                        pre_defined_reg = tmp[0]

                    
            if j.startswith('case') or j.startswith('casez') or j.startswith('casex'):
                #print(module_lists[i][module_lists[i].index(j)+1:])
                line_after_case = module_lists[i][module_lists[i].index(j)+1:module_lists[i].index(j)+2]
                
                # convert from list to string
                line_after_case = ''.join(line_after_case)
                # remove all characters before :
                line_after_case = line_after_case[line_after_case.find(':')+1:]
                #print(line_after_case)
                try:
                    if pre_defined_reg in line_after_case:
                        break
                except:
                    pass
                if "synopsys" in j:
                    break
                bound = j.find('e')
                reg_name = j[bound+1:]
                reg_name = reg_name.replace(' ', '')
                reg_name = reg_name.replace('(', '')
                reg_name = reg_name.replace(')', '')
                reg_name = reg_name.replace(':', '')
                reg_name = reg_name
                #print(reg_name)
                # take size of reg_name
                for k in reg_list:
                    if k[1] == reg_name and k[0] == i:
                        size = k[2]
                        size_list_for_case.append(size)
                        break
                case_i = module_lists[i].index(j)
                
                rows_count = 0
                
                for line in module_lists[i][case_i+1:]:
                    if line.startswith('endcase'):
                        break
                    if line.startswith('default'):
                        mask = 1
                        break
                    if ":" in line:
                        rows_count += 1
                #print("rows_count", rows_count)
                if mask == 0:
                    if pow(2, size) != rows_count:
                        print("\nNon-Full Case:")
                        for x in line_num_list:
                            if x[0] == i and x[2] == j:
                                line_num = x[1] + 1
                        print("Line Number:", line_num)
                        statement_lists.append("\nNon-Full Case")
                        statement_lists.append("Line Number : " + str(line_num))
                        print("Module", i + 1, ":", module_lists[i][0])
                        statement_lists.append("Module " + str(i + 1) + " : " + module_lists[i][0])
                        print(f"Size of reg \"{reg_name}\":", size) 
                        statement_lists.append(f"Size of reg \"{reg_name}\" : " + str(size))
                        print("Number of variations:", rows_count)
                        statement_lists.append("Number of variations : " + str(rows_count))
                        print("Expected number of variations:", pow(2, size))
                        statement_lists.append("Expected number of variations : " + str(pow(2, size)))
                        print("Number of variations is not equal to expected number of variations")
                        statement_lists.append("Number of variations is not equal to expected number of variations")
                        print("=====================================")
                        statement_lists.append("=====================================")
                        print()
                        break
                    else:
                        break
            
                          
#print(size_list_for_case)   
check_full_case(module_lists)

def word_position_relative_to_equal(word, sentence):
    search_pattern = r'\b{}\b'.format(word)

    matches = [match for match in re.finditer(search_pattern, sentence)]

    if matches:
        word_index = matches[0].start()
        equal_index = sentence.find('=')
        
        if sentence.count('=') > 1:
            return 3  # not found
        
        last_word_index = matches[-1].start() + len(matches[-1].group()) - 1
        
        if equal_index == -1:
            return 3  # not found
        
        if word_index < equal_index and last_word_index > equal_index:
            return 2  # found both before and after equal
        
        elif word_index < equal_index:
            return 0  # before equal
        
        elif last_word_index > equal_index:
            return 1  # after equal
    else:
        return 3  # not found
    
def reg_list_for_unintialized(module_lists):
    reg_names = [] # list of lists first place is reg name and second place is module index
    for i in module_lists:
        for j in i:
            if j.startswith('reg') and not('=' in j):
                mask = 1
                if "]" in j:
                    j = j[j.find(']')+1:]
                    if "," in j:
                        j = j.replace(",","")    
                j = j.replace("reg","")
                j = j.replace(";","")
                if j[0] == " ":
                    j = j[1:]
                if " " in j:
                    tmp = j.split(" ")
                    for t in tmp:
                        reg_names.append([t, module_lists.index(i)])
                else:
                    reg_names.append([j,module_lists.index(i)])
    return reg_names

def check_unintialized_reg(module_lists):
    mask = 0
    reg_names = reg_list_for_unintialized(module_lists)
#print(reg_names)
#print()
    for i in reg_names:
        module = module_lists[i[1]]
        #print(i[1])
        #print(i[0])
        mask = 0
        for j in module:
            if i[0] in j and not(j.startswith('case')):
                
                if word_position_relative_to_equal(i[0],j) == 0:
                    #print("before equal")
                    #print(j)
                    mask = 1
                elif word_position_relative_to_equal(i[0],j) == 1:
                    #print("after equal")
                    #print(j)
                    print("\nModule Name:", module[0])
                    for x in line_num_list:
                        if x[0] == i[1] and x[2] == j:
                            line_num = x[1] + 1
                    print("Line Number:", line_num)
                    statement_lists.append("\nModule Name: " + module[0])
                    statement_lists.append("Line Number : " + str(line_num))
                    print("Reg name: ", f"\"{i[0]}\"")
                    statement_lists.append("Reg name: " + f"\"{i[0]}\"")
                    print("Possible Uninitialized reg")
                    statement_lists.append("Possible Uninitialized reg")
                    print("=====================================")
                    statement_lists.append("=====================================")
                    #mask = 1
                elif word_position_relative_to_equal(i[0],j) == 2:
                    #print("both before and after equal")
                    #print(j)
                    print("\nModule Name:", module[0])
                    statement_lists.append("\nModule Name: " + module[0])
                    for x in line_num_list:
                        if x[0] == i[1] and x[2] == j:
                            line_num = x[1] + 1
                    print("Line Number:", line_num)
                    statement_lists.append("Line Number : " + str(line_num))
                    print("Reg name: ", f"\"{i[0]}\"")
                    statement_lists.append("Reg name: " + f"\"{i[0]}\"")
                    print("Possible Uninitialized reg")
                    statement_lists.append("Possible Uninitialized reg")
                    print("=====================================")
                    statement_lists.append("=====================================")
                    #mask = 1
                #print("--------------------")
            if mask == 1:
                break
            if j.startswith('case') and i[0] in j:
                #print(j)
                #print("case")
                print("\nModule Name:", module[0])
                statement_lists.append("\nModule Name: " + module[0])
                for x in line_num_list:
                    if x[0] == i[1] and x[2] == j:
                        line_num = x[1] + 1
                print("Line Number:", line_num)
                statement_lists.append("Line Number : " + str(line_num))
                print("Reg name: ", f"\"{i[0]}\"")
                statement_lists.append("Reg name: " + f"\"{i[0]}\"")
                print("Possible Uninitialized reg")
                statement_lists.append("Possible Uninitialized reg")
                print("=====================================")
                statement_lists.append("=====================================")
                break
                
            
check_unintialized_reg(module_lists)

def check_infer_latch(module_lists):
    line_count = 0

    for module_index, module in enumerate(module_lists, start=1):
        always_blocks = []
        used_signals = set()
        module_declaration_line = module[0]
        used_signals.update(set(re.findall(r'\b(\w+)\b', re.search(r'\bmodule\s+\w+\s*\((.*?)\);', module_declaration_line).group(1))))
        for i, line in enumerate(module):
            if re.search(r'always\s*@', line):
                always_blocks.append(i)

            
        for always_index in always_blocks:
            sensitivity_line = module[always_index]
            sensitivity_line = sensitivity_line.replace("always", "").replace("@", "").strip()

            # Extract the block content including the line with 'always' keyword
            block_content = [sensitivity_line] + module[always_index + 1:]

            # Check for latch inference scenarios
            check_sensitivity_list(sensitivity_line, module_index, line_count + always_index + 1, used_signals)
            check_feedback_loop(block_content, module_index, line_count + always_index + 1)
            check_if_without_else(block_content, module_index, line_count + always_index + 1)
            check_case_without_default(block_content, module_index, line_count + always_index + 1)

        # Update line_count for the next module
        line_count += len(module)
# Update the check_sensitivity_list function
def check_sensitivity_list(sensitivity_line, module_index, line_number, used_signals):
    # Check if sensitivity_line is "@*" or contains clk
    if "*" in sensitivity_line or "clk" in sensitivity_line:
        return

    # Extract signals from the sensitivity line
    sensitivity_list = re.findall(r'\b([a-zA-Z_]\w*)\b', sensitivity_line)
    # Remove non-signal elements from the sensitivity list
    sensitivity_list = [signal for signal in sensitivity_list if signal not in ["*", "("]]

    # Check for missing signals
    missing_signals = set()
    for signal in used_signals:
        if signal not in sensitivity_list:
            missing_signals.add(signal)

    for x in line_num_list:
        if sensitivity_line in x[2]:
            line_number = x[1] + 1

    # Print results
    if missing_signals:
        print(f"\nMay Infer Latch in module {module_index}, : {module_lists[module_index-1][0]} , line: {line_number}")
        statement_lists.append(f"May Infer Latch in module {module_index}, : {module_lists[module_index-1][0]} , line: {line_number}")
        print(f"Reason: Signal(s) missing in the sensitivity list: {', '.join(missing_signals)}")
        statement_lists.append(f"Reason: Signal(s) missing in the sensitivity list: {', '.join(missing_signals)}")
        print("=====================================")
        statement_lists.append("=====================================")
        return



def check_if_without_else(block_content, module_index, line_number):
    found_if = False
    found_else = False

    for line in block_content:
            if re.search(r'\bif\b', line):
                for x in line_num_list:
                    if line in x[2]:
                        line_number = x[1] + 1
                found_if = True
            
            # Check for 'else' inside 'always' block
            if found_if and re.search(r'\belse\b', line):
                found_else = True



    # If we reach here, it means 'if' was not followed by 'else' inside 'always' block
    if found_if and not found_else:
        print(f"\nInfer Latch in module {module_index}, : {module_lists[module_index - 1][0]}, line: {line_number}")
        statement_lists.append(f"Infer Latch in module {module_index}, : {module_lists[module_index - 1][0]}, line: {line_number}")
        print("Reason: 'if' statement without 'else' detected")
        statement_lists.append("Reason: 'if' statement without 'else' detected")
        print("=====================================")
        statement_lists.append("=====================================")

def check_case_without_default(block_content, module_index, line_number):
    found_case = False
    found_default = False

    for line in block_content:
        if re.search(r'^\s*case\b', line):
            if not re.search(r'//\s*synopsys\s*full_case', line):
                for x in line_num_list:
                    if line in x[2]:
                        line_number = x[1] + 1
                found_case = True

        if found_case and re.search(r'^\s*default\b', line):
                found_default = True

    if found_case and not found_default:
        print(f"\nMay Infer Latch in module {module_index},: {module_lists[module_index-1][0]}, line: {line_number}")
        statement_lists.append(f"May Infer Latch in module {module_index},: {module_lists[module_index-1][0]}, line: {line_number}")
        print("Reason: 'case' statement without 'default' detected")
        statement_lists.append("Reason: 'case' statement without 'default' detected")
        print("=====================================")
        statement_lists.append("=====================================")
        return

       

def check_feedback_loop(block_content, module_index, line_number):
    dependencies = {}  # Dictionary to store signal dependencies

    # Extract signal dependencies from the block content
    for line in block_content[1:]:  # Exclude the sensitivity line
       match = re.search(r'\b(\w+)\s*(<=|=)\s*(.+?)\s*;', line)
       if match:
            left_signal, operator, right_expr = match.groups()
            dependencies[left_signal] = re.findall(r'\b\w+\b', right_expr)

    # Check for feedback loops
    for signal in dependencies:
        if signal in dependencies[signal]:
            for x in line_num_list:
                if block_content[0] in x[2]:
                    line_number = x[1] + 1
            print(f"\nMay Infer Latch in module {module_index}, : {module_lists[module_index-1][0]}, line: {line_number}")
            statement_lists.append(f"\nMay Infer Latch in module {module_index}, : {module_lists[module_index-1][0]}, line: {line_number}")
            print("Reason: Combinational Feedback loop detected")
            statement_lists.append("Reason: Combinational Feedback loop detected")
            print("=====================================")
            statement_lists.append("=====================================")
            return


# Call the modified checker function
check_infer_latch(module_lists)

def extract_initial_values(module_lists):
    initial_values = {}
    # Improved regex pattern to capture Verilog style binary values
    initial_pattern = re.compile(r'\b(\w+)\s*=\s*(\d+\'b[01]+);')
    inside_initial_block = False
    for lines in module_lists:
        for line in lines:
            if 'initial' in line:
                inside_initial_block = True
            elif 'end' in line and inside_initial_block:
                inside_initial_block = False
            elif inside_initial_block:
                match = initial_pattern.search(line)
                if match:
                    var, value = match.groups()
                    initial_values[var] = value
    return initial_values

def normalize_bit_length(value):
    # Normalizing binary values to their simplest form for comparison
    # Example: from '2'b00' to '1'b0'
    match = re.match(r"(\d+)'b([01]+)", value)
    if match:
        bits, binary = match.groups()
        return f"{int(binary, 2)}"  # Returns the integer value of the binary
    return value

def analyze_verilog(module_lists):
    issues = {}
    current_module = None
    line_num = 0

    initial_values = extract_initial_values(module_lists)

    if_condition_pattern = re.compile(r'if\s*\(\s*(\w+)\s*==\s*(\d+\'b[01]+)\s*\)')
    for lines in module_lists:
        for line in lines:
            for x in line_num_list:
                if x[2] == line:
                    line_num = x[1] + 1
            match = re.search(r'module\s+(\w+)', line)
            if match:
                current_module = match.group(1)
                issues[current_module] = {
                    'unreachable_blocks': [],
                    'module_line_num': line_num,
                    'initial_values': initial_values.copy()
                }
                continue

            if not current_module:
                continue

            match = if_condition_pattern.search(line)
            if match:
                var, expected_value = match.groups()
                actual_value = issues[current_module]['initial_values'].get(var)

                # Normalizing the bit-length for comparison
                if actual_value and normalize_bit_length(actual_value) != normalize_bit_length(expected_value):
                    issues[current_module]['unreachable_blocks'].append((line_num, line, var, actual_value, expected_value))

    return issues

def report_issues(issues):
    for module, module_issues in issues.items():
        if module_issues['unreachable_blocks']:
            print(f"\nModule: {module}")
            statement_lists.append(f"\nModule: {module}")
            for line_num, line, var, actual_value, expected_value in module_issues['unreachable_blocks']:
                print(f"Unreachable Block")
                statement_lists.append(f"Unreachable Block")
                print(f"line {line_num}: {line}")
                statement_lists.append(f"line {line_num}: {line}")
                print(f"Variable '{var}' is initialized to {actual_value}, but the condition checks for {expected_value}.")
                statement_lists.append(f"Variable '{var}' is initialized to {actual_value}, but the condition checks for {expected_value}.")
            print('=====================================')  
            statement_lists.append('=====================================')

issues = analyze_verilog(module_lists)
report_issues(issues)

def check_multidriven_variables_always_blocks(module_lists):
    modules_with_multidriven_variables = set()

    for module_index, module in enumerate(module_lists, start=1):
        # Always blocks and their contents
        always_blocks = []

        # Extract contents of always blocks
        inside_always = False
        current_always_block = []

        for line in module:
            if 'always' in line:
                inside_always = True
                current_always_block = ['always']
            elif inside_always:
                current_always_block.append(line.strip())
                if 'end' in line:
                    inside_always = False
                    always_blocks.append(current_always_block)

        # Compare always blocks to identify multidriven variables
        seen_variables = set()
        seen_variables_list = []
        for i, block1 in enumerate(always_blocks):
            for j, block2 in enumerate(always_blocks):
                if i != j:
                    # Check for 'variable ='
                    for line1 in block1[2:-1]:  # Skip 'always', 'begin', 'end'
                        for line2 in block2[2:-1]:  # Skip 'always', 'begin', 'end'
                            seen_variables_list.append(line2)
                            if '=' in line1 and '=' in line2:
                                variable_name1 = line1.split('=')[0].strip()
                                variable_name2 = line2.split('=')[0].strip()
                                if variable_name1 == variable_name2:
                                    seen_variables.add(variable_name1)

        # Print the results only if there are multidriven variables in the module
        if seen_variables and module_index not in modules_with_multidriven_variables:
            modules_with_multidriven_variables.add(module_index)
            print(f"\nModule {module_index}:", module[0])
            statement_lists.append(f"\nModule {module_index}: {module[0]}")
            for block in always_blocks:
                print("Always Block:", block)
                statement_lists.append("Always Block: " + str(block))
                for n in block:
                    for x in line_num_list:
                        for y in seen_variables_list:
                            if x[2] == n and y in n:
                                line_num = x[1] + 1
                                print("Line Number:", line_num)
                                statement_lists.append("Line Number : " + str(line_num))
                                break
                        pass
                    
            print("Multidriven Variables:", seen_variables)
            statement_lists.append("Multidriven Variables: " + str(seen_variables))
            print("=====================")
            statement_lists.append("=====================")

# Example usage
check_multidriven_variables_always_blocks(module_lists)


def check_multidriven_variables_assign_statements(module_lists):
    for module_index, module in enumerate(module_lists, start=1):
        # Extracted variable names and sizes
        variables = set()
        # Assign statements and assigned variables
        assign_statements = []

        for line in module:
            # Check if the line contains an assign statement
            
            if 'assign' in line:
                parts = line.split()
                assign_index = parts.index('assign')

                # Extract the assigned variable name
                if assign_index < len(parts) - 1:
                    variable_name = parts[assign_index + 1].rstrip(';')
                    # Check if the variable is already assigned in another statement
                    if variable_name in variables:
                        assign_statements.append([line, variable_name])
                    else:
                        variables.add(variable_name)

        # Check for multidriven variables within the same module based on assign statements
        seen_variables = set()
        for statement, variable in assign_statements:
            # Check if the variable is repeated (multidriven) in the same module
            if variable in seen_variables:
                print(f"Module {module_index}: Variable '{variable}' is multidriven.")
            else:
                seen_variables.add(variable)

        # Print the results only if there are multidriven variables in the module
        if seen_variables:
            print(f"\nModule {module_index}:", module[0])
            statement_lists.append(f"\nModule {module_index}: {module[0]}")
            print("Assign Statements:", assign_statements)
            for n in assign_statements:
                for x in line_num_list:
                    if x[2] == n[0]:
                        line_num = x[1] + 1
                        print("Line Number:", line_num)
                        statement_lists.append("Line Number : " + str(line_num))
                        break
    
                        
                pass
            statement_lists.append("Assign Statements: " + str(assign_statements))
            print("Multidriven Variables:", seen_variables)
            statement_lists.append("Multidriven Variables: " + str(seen_variables))
            print("=====================")
            statement_lists.append("=====================")

# Example usage
check_multidriven_variables_assign_statements(module_lists)


def checkArithmeticOverflow(module_lists):
    # extracting the variables from the module
    variable_list = [[] for _ in range(len(module_lists))]
    
    for module_index, module in enumerate(module_lists, start=1):
        #print("Module Number:", module_index)
        for variable_declaration in module:
            # check if the variable is input, output, wire, or reg
            if variable_declaration.startswith(('input ', 'output ', 'wire ', 'reg ')):
                # Extract variable name and size
                parts = variable_declaration.split()
                parts[-1] =  parts[-1].rstrip(';')
                # Variable names are strings after '[number:number]' or after 'reg', 'wire', 'input', 'output'
                variable_names = [part.strip(',') for part in parts[1:] if part not in ('reg', 'wire', 'input', 'output')]
                for i in variable_names:
                    if '[' in i and ']' in i:
                        variable_names.remove(i)
                   

                index = 0
                for i in variable_names:
                    if '=' in i:
                        variable_names.pop(index)
                        variable_names.pop(index)
                    index += 1

                variable_size = 1  # Default size is 1
                
                # Check if [number-1:0] pattern is present
                if '[' in variable_declaration and ']' in variable_declaration:
                    size_part = variable_declaration.split('[')[1].split(']')[0]

                        # Extract the size correctly
                    if ':' in size_part:
                        sizes = size_part.split(':')
                        variable_size = abs(int(sizes[0]) - int(sizes[1])) + 1
                    else:
                        variable_size = int(size_part) + 1
                # Store the variable names and size
                variable_list[module_index - 1].extend([[name, variable_size] for name in variable_names if name])

        #print("Variable List:", variable_list[module_index - 1])
        

        # extracting the operations from the module
        operation_list = []
        for operation in module:
            if '=' in operation:
                if '+' in operation or '-' in operation or '*' in operation or '/' in operation:
                    # Extract the operation
                    parts = operation.split('=')
                    parts[-1] = parts[-1].rstrip(';')
                    parts = [part.split(' ') for part in parts]
                    # Remove empty strings
                    for part in parts:
                        while '' in part:
                            part.remove('')

                    print("Parts:", parts)

                    left_side_size = 0
                    right_side_size = 0
                    for variable in variable_list[module_index - 1]:
                        if variable[0] in parts[0]:
                            left_side_size = variable[1]
                            break
                    for variable in variable_list[module_index - 1]:
                        if variable[0] in parts[1]:
                            right_side_size = max(variable[1], right_side_size)
                    
                    binary_size = re.findall(r'\b(\d+\'b[01]+)\b', operation)
                    for i in binary_size:
                        size = i.split('\'')[0]
                        size = int(size)
                        if size > right_side_size:
                            right_side_size = size

                    
                

                    if left_side_size <= right_side_size:
                        print("\nPossible Arithmetic Overflow in module", module_index, ":", module[0])
                        statement_lists.append("\nPossible Arithmetic Overflow in module " + str(module_index) + " : " + module[0])
                        for x in line_num_list:
                            if x[0] == module_index-1 and x[2] == operation:
                                line_num = x[1] + 1
                        print("Line Number:", line_num)
                        statement_lists.append("Line Number : " + str(line_num))
                        print("Line: ", operation)
                        statement_lists.append("Line: " + operation)
                        print("Left side size:", left_side_size)
                        statement_lists.append("Left side size: " + str(left_side_size))
                        print("Right side size:", right_side_size)
                        statement_lists.append("Right side size: " + str(right_side_size))

                        

                        
                    operation_list.append(parts)


        if len(operation_list) == 0:
            pass
        else:
            print("Operation List:", operation_list)
            statement_lists.append("Operation List: " + str(operation_list))
            print("=====================")
            statement_lists.append("=====================")

        #print()
    
checkArithmeticOverflow(module_lists)

def extract_text_before_colon(input_text):
    # Find the index of the colon
    colon_index = input_text.find(':')

    if colon_index != -1:
        # Extract the text before the colon
        text_before_colon = input_text[:colon_index].strip()
        return text_before_colon
    else:
        return "None"
    
def can_be_number(input_text):
    try:
        input_text = input_text.replace(' ', '')
        if input_text[2] == 'b':
            input_text = input_text.split('b')[1]
            #print(input_text)
        elif input_text[2] == 'd':
            input_text = input_text.split('d')[1]
        elif input_text[2] == 'h':
            input_text = input_text.split('h')[1]
            input_text = int(input_text, 16)
        int(input_text)
        return True
    except :
        return False

def is_parallel_sequence(lst):
    lst0 = [element.replace('?', '0') for element in lst]
    lst0 = [element.replace('x', '0') for element in lst0]
    lst1 = [element.replace('?', '1') for element in lst]
    lst1 = [element.replace('x', '1') for element in lst1]

    set0 = set(lst0)
    set1 = set(lst1)
    if len(set0) < len(lst0) or len(set1) < len(lst1):
        return False
    else:
        return True
    
def check_parallel_case(module_lists):
    parallel_case = calculating_case_index(module_lists)
    mask2 = 0
    for i in parallel_case:
        mask = 0
        case_values = []
        for j in module_lists[i]:
            
            k_counter = 0
            parallel_case_counter = 0
            if j.startswith('case') or j.startswith('casez') or j.startswith('casex'):
            # iterate over lines after case
                #print(j)
                case_number = j
                if "synopsys" in j:
                    tmp = j.split(" ")
                    if "parallel_case" in tmp:
                        mask2 = 1
                        break
    
        
                for k in module_lists[i][module_lists[i].index(j)+1:]:
                    #print(k)
                    k_counter += 1
                    num = extract_text_before_colon(k)
                    if num != "None" and num != "default":
                        case_values.append(num)
                    if can_be_number(num):
                        parallel_case_counter += 1
                        #print("yes")
                    # mask = 1

                    if k.startswith('endcase'):
                        break
        
        for t in case_values:
            if can_be_number(t):
                mask = 1
            else:
                mask = 0
                break
        
        if mask == 0 and mask2 == 0 :
            if is_parallel_sequence(case_values) == False:
                print("Non-Parallel Case:")
                statement_lists.append("\nNon-Parallel Case:")
                print("Module", i + 1, ":", module_lists[i][0])
                statement_lists.append("Module " + str(i + 1) + " : " + module_lists[i][0])
                for x in line_num_list:
                    if x[0] == i and x[2] == case_number:
                        line_num = x[1] + 1
                print("Line Number:", line_num)
                statement_lists.append("Line Number : " + str(line_num))
                print("=====================================")
                statement_lists.append("=====================================")
                print()

        if mask2 == 1:
            mask2 = 0


check_parallel_case(module_lists)
def report_generator(statement_lists):
    with open('report.txt', 'w') as f:
        for item in statement_lists:
            f.write("%s\n" % item)
    print("Report Generated Successfully")
    
report_generator(statement_lists)




