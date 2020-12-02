from dbutils2 import register_into_db
import csv

if __name__ == '__main__':
    with open("CUSTOMER.txt", encoding='UTF-8') as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            print(row)
            register_into_db(row[2] + ' ' + row[3], row[1], row[4], 'entropy', 'Dhaka', '1998-15-06'
                             , 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fm.facebook.com%2Fthecuriousreaderbooks%2Fphotos%2F%3Ftab%3Dalbum%26album_id%3D131426517060084%26mt_nav%3D1&psig=AOvVaw1jyoAtCg5TsN4hWsvn5PMo&ust=1606568371239000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCOj45d3jou0CFQAAAAAdAAAAABAE'
                             , 'M')