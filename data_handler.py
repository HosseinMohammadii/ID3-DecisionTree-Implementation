import arff


class DataSet:

    def __init__(self, path):
        self.path = path
        self.data = None
        self.attributes = None

    def fill_by_arff(self, ):
        with open(self.path, 'r') as f:
            dataset = arff.load(f)
            self.data = [d for d in dataset['data']]
            self.attributes = dict(dataset['attributes'])

    @classmethod
    def get_sub_data_remove_attr(cls, data: list, attribute_index: int, value):
        old_data = data.copy()
        new_data = []

        for d in old_data:
            if d[attribute_index] == value:
                nd = []
                for i in range(0, len(d)):
                    if i == attribute_index:
                        continue
                    nd.append(d[i])
                new_data.append(nd)

        return new_data

    @classmethod
    def test_get_sub_data_remove_attr(cls):
        data = [['0', '1', '2', '1', '1'], ['10', '1', '4', '5', '1'], ['1', '1', '6', '8', '1'], ['20', '1', '13', '8', '1']]
        data2 = cls.get_sub_data_remove_attr(data, 3, '8')
        print(data2)

        data3 = cls.get_sub_data_remove_attr(data2, 1, '1')
        print(data3)

    @classmethod
    def print_data(cls, data):
        print('--------printing data--------')
        for d in data:
            print(d)

