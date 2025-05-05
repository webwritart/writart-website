from extensions import db
from models.quiz import Quiz


def add_quiz_data_to_db(file_path, category):
    f = file_path
    capitalized_category = category.capitalize()
    with open("quiz_data_log.txt", "a") as lf:
        lf.write("Entered add_quiz_data_to_db function\n")
    with open(f, 'rb') as file:
        with open("quiz_data_log.txt", "a") as lf:
            lf.write("quiz data file opened successfully\n")
        try:
            content = file.read()
        except Exception as e:
            with open("quiz_data_log.txt", "a") as lf:
                lf.write(f'{e}\n')
        with open("quiz_data_log.txt", "a") as lf:
            lf.write("File read successfully.\n")
        data = content.split(b'\n')
        with open("quiz_data_log.txt", "a") as lf:
            lf.write("data extracted successfully!\n")
        data.pop()
        option_index = ['a', 'b', 'c', 'd', 'e']
        file.close()

        for d in data:
            option_list = []
            q = d.split(b';;')[0]
            opt = d.split(b';;')[1].split(b'&')[0]
            opt_list = opt.split(b'*')
            for idx, opt in enumerate(opt_list)
                opt_idx = option_index[idx]
                option = f'{opt_idx}. {opt}'
                option_list.append(option)
            if len(option_list) == 2:
                for i in range(3):
                    option_list.append('')
            elif len(option_list) == 3:
                for i in range(2):
                    option_list.append('')
            elif len(option_list) == 4:
                option_list.append('')

            a_index = int(d.split(b';;')[1].split(b'&')[1])-1
            answer = option_index[a_index]
            with open("quiz_data_log.txt", "a") as lf:
                lf.write("Entered data loop.\n")

            entry = Quiz(
                question=q,
                option_a=option_list[0],
                option_b=option_list[1],
                option_c=option_list[2],
                option_d=option_list[3],
                option_e=option_list[4],
                answer=answer,
                category=capitalized_category,
                subcategory='',
                level='',
                time_played=0,
                time_correct=0
            )
            db.session.add(entry)
            with open("quiz_data_log.txt", "a") as lf:
                lf.write("Database 'entry' prepared.\n")
    db.session.commit()
    with open("quiz_data_log.txt", "a") as lf:
        lf.write("Added to database successfully.\n")
    return 'Success!'


