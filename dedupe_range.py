import numpy as np
import re
from textdistance import levenshtein

normalized_similarity = levenshtein.normalized_similarity

# Set of null values that should be ignored in score computation
NULL_VALUES = set(["", "None", "#N/A", "NA", " ", "  ", "-"])


def calculate_similarity(value, other, previous_score=1, weight=1, exact_match_weight=None):
    """Compares two values and returns the new similarity score

    Keyword arguments:
    value -- value to compare
    other -- other value to compare against
    previous_score -- previous score before factoring in the two values
    weight -- the relative weight to assign to the these values if similar (does not affect score if dissimilar)
    exact_match_weight -- weight given to completely identical values, defaults to weight
    """

    if previous_score == 0 or value in NULL_VALUES or other in NULL_VALUES:
        return previous_score

    if exact_match_weight is None:
        exact_match_weight = weight

    scaling_factor = (len(value) + len(other))/20
    # initial scaling factor based on length
    # 20 is an arbitrary factor here as a measurement of length of the field

    if value == other:
        scaling_factor *= exact_match_weight
        score = 2

    elif weight == 0:  # only identical matches matter
        return previous_score

    else:
        score = normalized_similarity(value, other)
        if score < 1:
            score = 0.5 + score
        else:
            score *= 2
            scaling_factor *= weight

    return previous_score*(score**scaling_factor)


v_calculate_similarity = np.vectorize(calculate_similarity)


class DedupeRange:

    def __init__(self, total_rows, start_row=0, end_row=None, source=None):
        """Initiates a class to process a range of rows for de-duplication

        Keyword arguments:
        total_rows -- the total number of rows in the file
        start_row -- the index to start at
        end_row -- the index to end at
        source -- a list detailing the source file of each row,
                    rows from the same source are not checked against each other
        """
        if end_row is None:
            end_row = total_rows

        self.processed_rows = end_row - start_row
        self.start_row = start_row
        self.end_row = end_row
        self.total_rows = total_rows

        self.score = np.tri(self.processed_rows, total_rows, start_row - 1)

        if source is not None:
            np_source = np.array(source)
            for i in range(start_row, end_row):
                self.score[i] *= np_source != source[i]

        self.column_count = 0

    def process(self, values, weight=1, exact_match_weight=1.5):
        """Processes a row of values

        Keyword arguments:
        values -- the list of values to look for duplicates
        weight -- the relative weight to assign to the these values if similar (does not affect score if dissimilar)
        exact_match_weight -- weight given to completely identical values, defaults to weight
        """

        values = np.array(values)

        for i in range(self.start_row, self.end_row):
            self.score[i] = v_calculate_similarity(
                values[i], values, self.score[i], weight, exact_match_weight)

    def process_UEN(self, values):

        def strip_value(value):
            # strip symbols and spaces
            stripped_value = re.sub('\W', '', value)
            # strip all letter prefixes
            stripped_value = re.sub('^[a-zA-Z]+', '', stripped_value)
            stripped_value = re.sub(
                '^[09]+', '', stripped_value)  # strip leading 0s and 9s
            stripped_value = re.sub(
                '[0]{2,}$', '', stripped_value)  # strip trailing 0s
            return stripped_value

        stripped_values = np.array([strip_value(value) for value in values])
        values = np.array(values)

        for i in range(self.start_row, self.end_row):
            self.score[i] = np.maximum(
                v_calculate_similarity(
                    stripped_values[i], stripped_values, self.score[i], 3, 3),
                v_calculate_similarity(values[i], values, self.score[i], 0, 4),
            )
