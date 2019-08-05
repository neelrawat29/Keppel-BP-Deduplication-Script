import sys
import re
from functools import reduce

import textdistance
from openpyxl import workbook, load_workbook


# TODO: better display of duplicates
class PotentialDuplicates:
    def __init__(self, other_row=None, col=None, message=None):
        self.potential_duplicates = {}
        self.score = {}
        if other_row is not None:
            self.addPotentialDuplicate(other_row, col, message)

    def addPotentialDuplicate(self, other_row, col, message):

        if other_row in self.potential_duplicates and not col in self.potential_duplicates[other_row]:
            self.potential_duplicates[other_row][col] = message

        else:
            self.potential_duplicates[other_row] = {col: message}

    def add_score(self, other_row, col, score):
        if other_row in self.score:
            if not (col in self.score[other_row]) or (col in self.score[other_row] and self.score[other_row][col] < score):
                self.score[other_row][col] = score
        else:
            self.score[other_row] = {col: score}

    def get_score(self):
        high_score = 0
        for other_row in self.score.values():
            current_score = 0
            for score in other_row.values():
                current_score += score
            if current_score > high_score:
                high_score = current_score

        return high_score

    def __str__(self):

        # list down problems from the most similar other row
        # find the highest count first

        string_representation = ""
        printed_rows = set()

        for _ in range(len(self.potential_duplicates)):
            if string_representation != "":
                string_representation += '\r\n'

            current_highest = 0

            for other_row, columns in self.potential_duplicates.items():
                if other_row not in printed_rows and len(columns) > current_highest:
                    current_highest = len(columns)
                    current_highest_row = other_row

            string_representation += '{}: {}'.format(current_highest_row, reduce(
                lambda x, y: x + ', ' + y, self.potential_duplicates[current_highest_row].values()))
            printed_rows.add(current_highest_row)


        return string_representation


class DedupFile:

    def __init__(self, file_name):
        print("Opening workbook %s" % file_name)
        wb = load_workbook(file_name)
        self.ws = wb.active
        # Copy entire workbook into memory as an easier-to-access data structure

        # Assume the first column is the ID, which will then be used to identify

        self.ids = []

        for cell_value in self.iter_row(1):
            self.ids.append(cell_value)

        self.potential_duplicates = [PotentialDuplicates() for _ in range(len(self.ids))]        

        print('Working on UEN')
        self.deduplicate_UEN(3)
        print('Working on col 4')
        self.deduplicate_column(4)
        print('Working on col 5')
        self.deduplicate_column(5)

        message_column = self.ws.max_column

        self.ws.cell(1, message_column).value = 'Messages'

        total_score = reduce(
            lambda acc, element: acc + element.get_score(), self.potential_duplicates, 0)
        print('Total score  is {} for {} rows (average {})'.format(
            total_score, len(self.ids), total_score/len(self.ids)))

        for row, dupes in enumerate(self.potential_duplicates):
            self.ws.cell(row+2, message_column).value = str(dupes)

        score_column = message_column + 1

        self.ws.cell(1, score_column).value = 'Similarity Score'

        for row, dupes in enumerate(self.potential_duplicates):
            self.ws.cell(row+2, score_column).value = dupes.get_score()

        wb.save(filename='output.xlsx')

    def deduplicate_column(self, column_no):
        column_name = self.ws.cell(1, column_no).value
        values = []
        for value in self.iter_row(column_no):
            values.append(value)

        for i, value in enumerate(values):
            for j, other in enumerate(values):
                # enforce first letter similarity
                if i <= j:
                    break

                if self.is_not_none(value) and value[0] == other[0]:

                    zlib_similarity = textdistance.zlib_ncd.normalized_similarity(
                        value, other)
                    ro_similarity = textdistance.ratcliff_obershelp.normalized_similarity(
                        value, other)
                    dl_similarity = textdistance.damerau_levenshtein.normalized_similarity(
                        value, other)

                    #self.add_score(i, column_no, j, zlib_similarity)
                    #self.add_score(i, column_no, j, ro_similarity)
                    #self.add_score(i, column_no, j, dl_similarity)

                    if value == other:
                        self.note_potential_dupe(
                            i, column_no, self.ids[j], '{} same as {}'.format(column_name, other))
                        self.note_potential_dupe(
                            j, column_no, self.ids[i], '{} same as {}'.format(column_name, value))
                        self.add_score(i, column_no, j, 1.5)

                    elif zlib_similarity >= 0.75:
                        self.note_potential_dupe(
                            i, column_no, self.ids[j], '{} similar to {}'.format(column_name, other))
                        self.note_potential_dupe(
                            j, column_no, self.ids[i], '{} similar to {}'.format(column_name, value))
                    # stopped using ratcliff because it doesn't really help? But it does pick up quite a few hits that were otherwise missed.
                    elif ro_similarity >= 0.80:
                        self.note_potential_dupe(
                            i, column_no, self.ids[j], '{} similar to {}'.format(column_name, other))
                        self.note_potential_dupe(
                            j, column_no, self.ids[i], '{} similar to {}'.format(column_name, value))
                    elif dl_similarity >= 0.75:
                        # print('DL detects extra {} and {}'.format(value, other))
                        self.note_potential_dupe(
                            i, column_no, self.ids[j], '{} similar to {}'.format(column_name, other))
                        self.note_potential_dupe(
                            j, column_no, self.ids[i], '{} similar to {}'.format(column_name, value))

        return

    def deduplicate_UEN(self, column_no):
        column_name = self.ws.cell(1, column_no).value

        values = []
        for value in self.iter_row(column_no):
            # strip symbols and spaces
            stripped_value = re.sub('\W', '', value)
            stripped_value = re.sub(
                '^[09]+', '', stripped_value)  # strip leading 0s and 9s
            stripped_value = re.sub(
                '[0]{2,}$', '', stripped_value)  # strip trailing 0s

            values.append((value, stripped_value))

        for i, (value, stripped_value) in enumerate(values):
            for j, (other, stripped_other) in enumerate(values):
                if i <= j:
                    break

                if self.is_not_none(value):
                    if value == other:
                        self.note_potential_dupe(
                            i, column_no, self.ids[j], '{} same as {}'.format(column_name, other))
                        self.note_potential_dupe(
                            j, column_no, self.ids[i], '{} same as {}'.format(column_name, value))
                        self.add_score(i, column_no, j, 5)

                    elif stripped_value == stripped_other:
                        self.note_potential_dupe(
                            i, column_no, self.ids[j], '{} similar to {}'.format(column_name, other))
                        self.note_potential_dupe(
                            j, column_no, self.ids[i], '{} similar to {}'.format(column_name, value))

                        self.add_score(i, column_no, j, ((len(
                            stripped_value) + len(stripped_other))/(len(value) + len(other))/2 + 0.5)*4)

                    elif len(stripped_value) >= 6:
                        dl_distance = textdistance.damerau_levenshtein.distance(
                            stripped_value, stripped_other)
                        self.add_score(i, column_no, j, (len(
                            stripped_value) + len(stripped_other) - dl_distance * 2)/(len(value) + len(other))/2*4)
                        if dl_distance <= 1 or (len(stripped_value) >= 9 and dl_distance <= 2):
                            self.note_potential_dupe(
                                i, column_no, self.ids[j], '{} similar to {}'.format(column_name, other))
                            self.note_potential_dupe(
                                j, column_no, self.ids[i], '{} similar to {}'.format(column_name, value))

    def note_potential_dupe(self, row, col, other, message):
        self.potential_duplicates[row].addPotentialDuplicate(
            other, col, message)

    def add_score(self, row, col, other_row, score):
        self.potential_duplicates[row].add_score(other_row, col, score)
        self.potential_duplicates[other_row].add_score(row, col, score)

    def iter_row(self, column_no):
        for cell in self.ws.iter_rows(min_row=2, min_col=column_no, max_col=column_no, values_only=True):
            yield str(cell[0])

    @staticmethod
    def is_not_none(value):
        null_values = set(["", "None", "#N/A", "NA", " ", "-"])
        return value not in null_values


file_name = sys.argv[1]

dedup = DedupFile(file_name)