import math
import random
from colorama import Fore, Back, Style

from data_handler import DataSet


class Attribute:
    def __init__(self, name, values, index_in_data):
        self.name = name
        self.values: iter = values
        self.index_in_data = index_in_data

    def __hash__(self):
        return hash((self.name, self.index_in_data))

    def __eq__(self, other):
        return (self.name, self.index_in_data) == (other.name, other.index_in_data)

    def decrease_index(self):
        self.index_in_data -= 1
        assert self.index_in_data >= 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def copy(self, delta_index):
        return Attribute(self.name, self.values, self.index_in_data + delta_index)


class Node:
    def __init__(self, attribute=None, node_type=None, answer=None):
        self.attribute: Attribute = attribute
        self.branches = {}
        self.node_type = node_type  # 'leave' or 'normal'
        self.answer: str = answer

        # self.arrive_value = None # Just for printing

    def add_branch(self, value, next_node):
        self.branches[value] = next_node


class ID3:

    def __init__(self, data, attributes: iter, label_attribute):
        self.data = data
        self.attributes: list = attributes
        self.root = None
        self.label_attribute: Attribute = label_attribute

    def cal_main_entropy(self):
        attribute = self.label_attribute
        attribute_each_value_count = {}
        all_rows_count = 0
        for row in self.data:
            all_rows_count += 1
            try:
                attr_value = row[attribute.index_in_data]
            except Exception as e:
                raise e

                # print('------------------------------------------------------------------------------------------')
                # print(self.attributes, self.label_attribute, self.label_attribute.index_in_data, '\n',
                #       all_rows_count, '\n', self.data[all_rows_count - 1], '\n', row, '\n',
                #       )

            attribute_each_value_count[attr_value] = attribute_each_value_count.get(attr_value, 0) + 1

        entropy = 0
        for attr_value, value_count in attribute_each_value_count.items():
            entropy = -1 * value_count / all_rows_count * math.log2(value_count / all_rows_count)
            assert entropy >= 0

        return entropy

    def cal_gain(self, attribute, main_entropy):

        """
        attr: sunny
        attr_value_count_dict = {
            yes: 13,
            no: 16,
        }
        """
        attr_value_count_dict = {}

        """
        attr: sunny , label: go out
        
        attr_value_label_value_count_dict = {
            yes: { yes: 10, no: 3},
            no: { yes: 4, no: 12},
        }
        """
        attr_value_label_value_count_dict = {}

        for attr_value in attribute.values:
            attr_value_label_value_count_dict[attr_value] = {}
            for label_value in self.label_attribute.values:
                attr_value_label_value_count_dict[attr_value][label_value] = 0

            attr_value_count_dict[attr_value] = 0

        all_rows_count = 0
        for row in self.data:
            all_rows_count += 1
            attr_value = row[attribute.index_in_data]
            label_value = row[self.label_attribute.index_in_data]
            attr_value_label_value_count_dict[attr_value][label_value] += 1
            attr_value_count_dict[attr_value] += 1

        entropy = 0
        for attr_value in attribute.values:
            attr_value_count = attr_value_count_dict[attr_value]
            attr_value_p = attr_value_count / all_rows_count
            t = 0
            for label_value in self.label_attribute.values:
                attr_value_label_value_count = attr_value_label_value_count_dict[attr_value][label_value]
                # print(attr_value, label_value, attr_value_count, attr_value_label_value_count)
                if attr_value_count == 0 or attr_value_label_value_count == 0:
                    continue
                t += -1 * attr_value_label_value_count / attr_value_count * math.log2(
                    attr_value_label_value_count / attr_value_count)
            t *= attr_value_p
            entropy += t
        assert entropy >= 0

        return main_entropy - entropy

    def cal_gains(self, main_entropy):
        gains = []

        # attr: Attribute
        for attr in self.attributes:
            if attr == self.label_attribute:
                continue
            gains.append((attr, self.cal_gain(attr, main_entropy)))
        return gains

    def find_max_gain_attr(self, gains) -> tuple:
        sorted_gain = sorted(gains, key=lambda x: x[1], reverse=True)
        return sorted_gain[0]

    def create_tree(self):
        # print(self.attributes)
        # DataSet.print_data(self.data)
        if not self.data or len(self.data) == 0:
            # print('empty')
            return Node(None, 'empty', None)

        if self.check_leave():
            # print('leave')
            return Node(None, 'leave', answer=self.get_answer())

        main_entropy = self.cal_main_entropy()
        if main_entropy == 0:
            # print('leave')
            return Node(None, 'leave', answer=self.get_answer())

        gains = self.cal_gains(main_entropy)
        best_attr, max_gain = self.find_max_gain_attr(gains)
        # print(best_attr, max_gain)
        self.root: Node = Node(best_attr, 'normal', None)
        sub_attributes, new_label_attribute = self.get_new_attributes(best_attr)
        for value in best_attr.values:
            sub_data = DataSet.get_sub_data_remove_attr(self.data, best_attr.index_in_data, value)
            # print('branch_value', value)
            sub_tree = ID3(sub_data, sub_attributes, new_label_attribute)
            node = sub_tree.create_tree()

            if node.node_type != 'empty':
                self.root.add_branch(value, node)

        return self.root

    def check_leave(self) -> bool:
        """
        is leave or not
        :return:
        """
        first_val = self.data[0][self.label_attribute.index_in_data]
        for row in self.data:
            if row[self.label_attribute.index_in_data] != first_val:
                return False
        return True

    def get_answer(self):
        return self.data[0][self.label_attribute.index_in_data]

    def get_new_attributes(self, removal_attribute: Attribute):
        new_attributes = []
        new_label_attribute = None
        for attr in self.attributes:
            if attr == removal_attribute:
                # print('remove removal attribute', removal_attribute, removal_attribute.index_in_data)
                continue
            if attr.index_in_data > removal_attribute.index_in_data:
                new_attr = attr.copy(-1)
                if attr == self.label_attribute:
                    new_label_attribute = new_attr
            else:
                new_attr = attr.copy(0)
                if attr == self.label_attribute:
                    new_label_attribute = new_attr

            new_attributes.append(new_attr)
        # print('new_label_attribute', new_label_attribute, new_label_attribute.index_in_data)
        # for a in new_attributes:
        #     print(a.index_in_data, end=', ')
        # print()

        return new_attributes, new_label_attribute

    def inference(self, row, test_attributes):
        return self.inference_node(self.root, row, test_attributes)

    def inference_node(self, node: Node, row, test_attributes):
        if node.node_type == 'empty':
            return random.choice(self.label_attribute.values)

        if node.node_type == 'leave':
            return node.answer

        node_attr_index_in_input = None
        for t_attr in test_attributes:
            if node.attribute.name == t_attr.name:
                node_attr_index_in_input = t_attr.index_in_data

        if node_attr_index_in_input is None:
            raise Exception('Attribute {} not included in the test'.format(node.attribute.name))

        try:
            next_node = node.branches[row[node_attr_index_in_input]]
            return self.inference_node(next_node, row, test_attributes)
        except Exception:
            return random.choice(self.label_attribute.values)

    def test_data(self, data, test_attributes, label_attribute):
        right_answer = 0
        wrong_answer = 0

        for row in data:
            answer = self.inference(row, test_attributes)
            if answer == row[label_attribute.index_in_data]:
                right_answer += 1
            else:
                wrong_answer += 1
        print('\n\n')
        print(Fore.GREEN + 'right_answer:', right_answer, Style.RESET_ALL + '-',
              Fore.RED + 'wrong_answer:', wrong_answer)


        accuracy_number = right_answer / (right_answer + wrong_answer) * 100

        raw_accuracy = '#'.rjust(30, '#') + '\n' + \
                   '####' + ('Accuracy: ' + "{:.2f} %".format(accuracy_number)).center(22) + '####' '\n' + \
                   '#'.rjust(30, '#')

        if accuracy_number > 65:
            accuracy = Fore.LIGHTGREEN_EX + raw_accuracy
        else:
            accuracy = Fore.LIGHTRED_EX + raw_accuracy

        print(accuracy)

    def print_tree(self):
        self.print_node(self.root)

    def print_node(self, node: Node, parent_str=''):
        if node.node_type == 'empty':
            return

        if node.node_type == 'leave':
            print(parent_str, end='')
            print('{0: ^10}'.format(Fore.CYAN + node.answer))

        for value in sorted(node.branches.keys()):
            att = '{0: ^8}'.format(Style.RESET_ALL + node.attribute.name)
            val = '{0: ^10}'.format(Fore.LIGHTYELLOW_EX + f'--{value}--> ')
            down_parent_str = parent_str + att + ' ' + val
            self.print_node(node.branches[value], down_parent_str)
