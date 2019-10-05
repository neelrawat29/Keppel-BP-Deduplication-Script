import numpy as np
import re
import textdistance
from tqdm import tqdm

normalized_similarity = textdistance.levenshtein.normalized_similarity

# Set of null values that should be ignored in score computation
NULL_VALUES = set(["", "None", "#N/A", "NA", " ", "  ", "-"])


def calculate_similarity(value, other, score_previous=1, weight=1, weight_exact_match=None):
    """Compares two values and returns the new similarity score

    Keyword arguments:
    value -- value to compare
    other -- other value to compare against
    score_previous -- previous score before factoring in the two values
    weight -- relative weight assigned to the these values, higher weights doesn't affect negative scores
    weight_exact_match -- weight given to completely identical values, defaults to weight
    """

    if score_previous == 0 or value in NULL_VALUES or other in NULL_VALUES:
        return score_previous

    if weight_exact_match is None:
        weight_exact_match = weight

    scaling_factor = (len(value) + len(other))/20
    # initial scaling factor based on length
    # 20 is an arbitrary factor here as a measurement of length of the field

    if value == other:
        scaling_factor *= weight_exact_match
        score = 2

    elif weight == 0:  # only identical matches matter
        return score_previous

    else:
        score = normalized_similarity(value, other)
        if score < 1:
            score = 0.5 + score
            scaling_factor *= weight if weight < 1 else 1
        else:
            score *= 2
            scaling_factor *= weight

    return score_previous*(score**scaling_factor)


v_calculate_similarity = np.vectorize(calculate_similarity)


class DedupeRange:

    def __init__(self, rows_total, row_start=0, row_end=None, source=None):
        """Initiates a class to process a range of rows for de-duplication

        Keyword arguments:
        rows_total -- the total number of rows in the file
        row_start -- the index to start at
        row_end -- the index to end at
        source -- a list detailing the source file of each row,
                    rows from the same source are not checked against each other
        """
        if row_end is None:
            row_end = rows_total

        self.rows = row_end - row_start
        self.row_start = row_start
        self.row_end = row_end
        self.rows_total = rows_total

        self.score = np.tri(self.rows, rows_total, row_start - 1)

        if source is not None:
            np_source = np.array(source)
            for row in self.range_rows('Initializing'):
                i = row - row_start
                self.score[i] *= np_source != source[row]

        self.col_count = 0
        self.pid = round(row_end/self.rows)

    def range_rows(self, desc=None):
        """An iterator for the rows. Also displays a progress bar if it is the first process."""
        if self.row_start == 0:
            return tqdm(range(self.row_start, self.row_end), desc=desc)
        return range(self.row_start, self.row_end)

    def process(self, values, weight=1, weight_exact_match=1.5):
        """Processes a row of values

        Keyword arguments:
        values -- the list of values to look for duplicates
        weight -- relative weight assigned to the these values, higher weights doesn't affect negative scores
        weight_exact_match -- weight given to completely identical values, defaults to weight
        """
        self.col_count += 1

        values = np.array(values)

        for row in self.range_rows('Col {}'.format(self.col_count)):
            i = row - self.row_start
            self.score[i] = v_calculate_similarity(
                values[row], values, self.score[i], weight, weight_exact_match)

    def process_UEN(self, values):
        self.col_count += 1

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

        for row in self.range_rows('UEN'):
            i = row - self.row_start
            self.score[i] = np.maximum(
                v_calculate_similarity(
                    stripped_values[row], stripped_values, self.score[i], 3, 3),
                v_calculate_similarity(
                    values[row], values, self.score[i], 0, 4),
            )
