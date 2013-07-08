#!/usr/bin/env python

import argparse
import sys
import csv
import datetime

# http://www.makeuseof.com/tag/how-to-migrate-from-shelfari-to-goodreads/


def main(shelfari_path):

    # opens shelfari file for reading, creates output file
    with open(shelfari_path, 'rb') as tsvin, open('out.csv', 'wb') as csvout:
        tsvin = csv.reader(tsvin, delimiter='\t')
        csvout = csv.writer(csvout)

        # gets heading of shelfari tsv
        heading = tsvin.next()

        # redundant columns list (columns to remove)
        ignore_columns = ['EditionId', 'ASIN', 'Favorites list',
                          'I plan to read list', 'Wish list',
                          "I've read list", 'I own list', "I'm reading list",
                          'PurchasePrice', 'Signed', 'Loaned', 'LoanedTo',
                          'LoanedDate', 'LoanDueDate', 'Private']

        # redundant columns indexes
        ignore_dict = {}
        for i in ignore_columns:
            ignore_dict[i] = heading.index(i)
        ignore_ids = ignore_dict.values()
        ignore_ids.sort()
        ignore_ids.reverse()

        # date columns indexes
        dates_dict = {}
        date_columns = ['DateRead', 'DateAdded', 'DatePurchased']
        for d in date_columns:
            dates_dict[d] = heading.index(d)

        # rename columns
        heading = [h.replace('Edition Author', 'TEMPNAME') for h in heading]
        heading = [h.replace('Author', 'Author l-f') for h in heading]
        heading = [h.replace('TEMPNAME', 'Author') for h in heading]
        heading = [h.replace('Rating', 'My Rating') for h in heading]
        heading = [h.replace('PublicationYear', 'Year Published')
                   for h in heading]
        heading = [h.replace('Note', 'Private Notes') for h in heading]
        heading = [h.replace('DateRead', 'Date Read') for h in heading]
        heading = [h.replace('DateAdded', 'Date Added') for h in heading]
        heading = [h.replace('DatePurchased', 'Original Purchase Date')
                   for h in heading]

        # removes redundant colums from heading
        for i in ignore_columns:
            heading.remove(i)

        # add Bookshelves column to heading
        heading.append('Bookshelves')

        # write heading to csv
        csvout.writerows([heading])

        # write rows to csv
        for row in tsvin:
            # choose a bookshelf for book
            if 'True' in row[ignore_dict['I plan to read list']]:
                row.append('to-read')
            elif 'True' in row[ignore_dict["I've read list"]]:
                row.append('read')
            elif 'True' in row[ignore_dict["I'm reading list"]]:
                row.append('currently-reading')
            else:
                row.append('unsorted')

            # convert dates to EU format
            row[dates_dict['DateRead']] = \
                convert_date(row[dates_dict['DateRead']])
            row[dates_dict['DateAdded']] = \
                convert_date(row[dates_dict['DateAdded']])
            row[dates_dict['DatePurchased']] = \
                convert_date(row[dates_dict['DatePurchased']])

            # remove redundant columns
            for ign_id in ignore_ids:
                row.pop(ign_id)

            # finally write row to csv
            csvout.writerows([row])

    print("Convert OK! :)\n")
    print("Visit http://www.goodreads.com/review/import to import your data")


def convert_date(date):
    """Converts date to YYYY/MM/DD format"""
    if date:
        return datetime.datetime.strptime(date, "%m/%d/%Y").\
            strftime("%Y/%m/%d")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Helps to migrate from Shelfari to Goodreads')
    parser.add_argument('filename', type=str,
                        help='TSV file exported from Shelfari\n'
                        'http://www.shelfari.com/profilesettings/shelf')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    main(args.filename)
