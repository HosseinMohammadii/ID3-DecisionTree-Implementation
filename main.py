from data_handler import DataSet
from desicion_tree import Attribute
from desicion_tree import ID3
import os


def attr_dict_to_attr_list(attributes_dict):
    attributes_list = []
    index = 0
    for attr in attributes_dict.keys():
        attributes_list.append(Attribute(attr, attributes_dict[attr], index))
        index += 1
    return attributes_list


clearConsole = lambda: os.system('clear')

if __name__ == '__main__':
    files = os.listdir('data_directory/')
    files = sorted(files)
    for i, file in enumerate(files):
        print('{0: <8}'.format(f'[{i}]:'), file)

    train_file_index = int(input('Enter a number to training: '))
    clearConsole()

    dataset = DataSet(os.path.join('data_directory', files[train_file_index]))
    dataset.fill_by_arff()
    attributes = attr_dict_to_attr_list(dataset.attributes)
    tree = ID3(dataset.data, attributes, attributes[6])
    tree.create_tree()

    for i, file in enumerate(files):
        print('{0: <8}'.format(f'[{i}]:'), file)
    test_file_index = int(input('Enter a number to test the tree: '))
    clearConsole()
    test_dataset = DataSet(os.path.join('data_directory', files[test_file_index]))
    test_dataset.fill_by_arff()
    test_attributes = attr_dict_to_attr_list(test_dataset.attributes)
    # tree.test_data([['1', '1', '1', '1', '4', '2', '1']], test_attributes, attributes[6])
    tree.test_data(test_dataset.data, test_attributes, attributes[6])

    tree.print_tree()
    # DataSet.test_get_sub_data_remove_attr()
