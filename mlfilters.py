__author__ = 'abkhanna'
import Store
import numpy
from sklearn.neighbors import KNeighborsClassifier


class NearestNeighborFilter:
    # this is the class that will implement the nearest neighbor filtering
    # on the incoming data stream.
    def __init__(self):
        self.records = list(Store.Record.fetch())

    def assign_indices(self):
        # pull from the Record object and build a index mapping for each word based on the total set
        # in the database
        mapping = {}
        class_mapping = []
        index_in_vector = 0
        for record in self.records:
            for key in record["vector"]:
                if key not in mapping:
                    mapping[key] = index_in_vector
                    index_in_vector += 1
            class_mapping.append(record["class"])

        return mapping, class_mapping

    def build_data_set(self):
        # this will build out the numpy arrays that we will use in the knearest neighbor analysis.
        mapping, class_set = self.assign_indices()
        data_set = []
        for record in self.records:
            vector = numpy.zeros(len(mapping))
            for key, value in record['vector'].iteritems():
                try:
                    index = mapping[key]
                    vector[index] += value
                except:
                    continue
            # append it to the list of vectors making the dataset
            data_set.append(vector)
        return data_set, class_set

    def dimensionalize_vector(self, input_vector):
        # input vector of the form of Counter({'some':1,...})
        # ignore class_map
        mapping = self.assign_indices()[0]  # tuple of (mapping, class_map)
        output_vector = numpy.zeros(len(mapping))
        for key, value in input_vector.iteritems():
            try:
                # not all the words in this vector will exist in the data set
                # only consider the ones that are in the dataset to compare on the same dimensions
                index = mapping[key]
                output_vector[index] += value
            except:
                continue
        return output_vector

    def classify(self, input_vector):
        # this function will classify the vectors into their appropriate class and report
        # zero or one based on the classification (0 -> invalid, 1 -> valid)
        # input_vector needs to be converted t the appropriate form.
        # this is the Counter() form of the vector
        vector = self.dimensionalize_vector(input_vector)
        data_set, class_set = self.build_data_set()
        print "Data Set: {0}\n\n Class Set: {1}\n\n".format(data_set, class_set)
        neigh = KNeighborsClassifier(n_neighbors=3)
        neigh.fit(data_set, class_set)
        predicted_class = neigh.predict(vector)
        print "Predicted class: {0}\n\n".format(predicted_class)
        return predicted_class
