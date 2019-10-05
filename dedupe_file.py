import sys
import numpy as np

import textdistance
from openpyxl import workbook, load_workbook

from tqdm import tqdm


from dedupe_range import DedupeRange


def dedupe_file(file_path, ignore_same_source=False):

    print("Opening workbook %s" % file_path)
    wb = load_workbook(file_path)
    ws = wb.active

    def iter_col(column_no):
        '''Helper function to iterate through a column of the excel workbook'''
        return [str(cell[0]).upper() for cell in ws.iter_rows(min_row=2, min_col=column_no, max_col=column_no, values_only=True)]

    ids = iter_col(1)
    source = iter_col(2)

    dedupe_range = DedupeRange(
        len(ids), source=source if ignore_same_source else None)

    dedupe_range.process_UEN(iter_col(3))
    dedupe_range.process(iter_col(4))
    dedupe_range.process(iter_col(5))
    dedupe_range.process(iter_col(6), weight=0.5, exact_match_weight=0.5)

    score = dedupe_range.score

    score += np.flipud(np.rot90(score))

    total_score = sum(np.max(score, axis=0))
    print('Total score  is {} for {} rows (average {})'.format(
        total_score, len(ids), total_score/len(ids)))

    score_column = ws.max_column + 1

    ws.cell(1, score_column).value = 'Similarity Score'

    for i, max_score in enumerate(np.max(score, axis=0)):
        ws.cell(i+2, score_column).value = max_score

    wb.save(filename='output.xlsx')

if __name__ == "__main__":
    file_path = sys.argv[1]

    ignore_same_source = False if len(sys.argv) <= 2 else sys.argv[2]

    dedupe_file(file_path, ignore_same_source)