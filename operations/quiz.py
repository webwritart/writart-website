from extensions import db
from models.quiz import Quiz


def add_quiz_data_to_db(file_path, category):
    f = file_path
    capitalized_category = category.capitalize()
    with open(f, 'r') as file:
        content = file.read()
        file.close()
        data = content.split('\n')
        data.pop()
        option_index = ['a', 'b', 'c', 'd', 'e']

        for d in data:
            option_list = []
            q = d.split(';;')[0]
            opt = d.split(';;')[1].split('&')[0]
            opt_list = opt.split('*')
            for idx, opt in enumerate(opt_list):
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

            a_index = int(d.split(';;')[1].split('&')[1])-1
            answer = option_index[a_index]

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
    db.session.commit()
    return 'Success!'


