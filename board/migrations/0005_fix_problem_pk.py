from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0004_remove_meet_theme'),
    ]

    operations = [
        # Step 1: Add new auto id column (nullable first so existing rows are ok)
        migrations.AddField(
            model_name='problem',
            name='id',
            field=models.IntegerField(null=True),
        ),
        # Step 2: Populate id values from rowid using raw SQL
        migrations.RunSQL(
            "UPDATE board_problem SET id = rowid;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Step 3: Make id the new primary key by recreating the table
        migrations.RunSQL(
            sql="""
                CREATE TABLE board_problem_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link VARCHAR(500) NOT NULL UNIQUE,
                    platform VARCHAR(100) NOT NULL,
                    solution_link VARCHAR(500) NOT NULL,
                    difficulty VARCHAR(100) NOT NULL,
                    difficulty_number REAL NULL
                );
                INSERT INTO board_problem_new (id, link, platform, solution_link, difficulty, difficulty_number)
                SELECT id, link, platform, solution_link, difficulty, difficulty_number
                FROM board_problem;
                DROP TABLE board_problem;
                ALTER TABLE board_problem_new RENAME TO board_problem;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Step 4: Fix the M2M through tables to reference the new int pk
        migrations.RunSQL(
            sql="""
                CREATE TABLE board_problem_meets_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id INTEGER NOT NULL REFERENCES board_problem(id),
                    meet_id INTEGER NOT NULL REFERENCES board_meet(id)
                );
                INSERT INTO board_problem_meets_new (problem_id, meet_id)
                SELECT p.id, m.meet_id
                FROM board_problem_meets m
                JOIN board_problem p ON p.link = m.problem_id;
                DROP TABLE board_problem_meets;
                ALTER TABLE board_problem_meets_new RENAME TO board_problem_meets;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE board_problem_categories_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id INTEGER NOT NULL REFERENCES board_problem(id),
                    algorithmcategory_id INTEGER NOT NULL REFERENCES cheatsheet_algorithmcategory(id)
                );
                INSERT INTO board_problem_categories_new (problem_id, algorithmcategory_id)
                SELECT p.id, c.algorithmcategory_id
                FROM board_problem_categories c
                JOIN board_problem p ON p.link = c.problem_id;
                DROP TABLE board_problem_categories;
                ALTER TABLE board_problem_categories_new RENAME TO board_problem_categories;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Step 5: Tell Django the field is now a proper AutoField pk
        migrations.AlterField(
            model_name='problem',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='link',
            field=models.CharField(max_length=500, unique=True),
        ),
    ]
