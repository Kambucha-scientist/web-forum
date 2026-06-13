--
-- PostgreSQL database dump
--

\restrict ydCGHQrhGoClVghm8QDx6JuFIejeJVc81epGeJyvMmSDYndq1csWvf9LJZPVY8Z

-- Dumped from database version 16.12
-- Dumped by pg_dump version 16.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.alembic_version (version_num) VALUES ('27245bb30f4e');


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.sections (id, title, description, codename, "group", created_at, is_visible) VALUES ('b885b475-9af3-4048-a5d6-bb9788b9473d', 'Python', 'Всё о языке программирования Python: от первых строк кода до сложных проектов. Обсуждаем синтаксис, библиотеки (Django, NumPy, Flask и др.), решаем задачи, разбираем ошибки и делимся опытом.', 'py', 'language', '2026-06-08 18:54:03.000951', true);
INSERT INTO public.sections (id, title, description, codename, "group", created_at, is_visible) VALUES ('ca365202-53a3-4ccc-8fc7-7aaea25549a1', 'Общее', 'Всё, что не вошло в другие разделы: общение, обсуждение новостей, жизненные ситуации, юмор, опросы и любые темы, не связанные с программированием. Главное — уважать друг друга и не нарушать правила. Добро пожаловать в свободную беседу!', 'b', 'AOB', '2026-06-08 19:00:00.560181', true);
INSERT INTO public.sections (id, title, description, codename, "group", created_at, is_visible) VALUES ('90e9f9f4-8497-4737-9c5d-858b58d31dbf', 'Тест', 'Тестовый раздел', 'test', 'DB', '2026-06-06 15:36:01.828385', false);
INSERT INTO public.sections (id, title, description, codename, "group", created_at, is_visible) VALUES ('5ad28274-8b1b-4960-a694-5ab3bde969f5', 'MySQL', 'Решение проблем и обсуждение MySQL/MariaDB. Тюнинг, репликация, оптимизация запросов, бэкапы, InnoDB, миграции с PostgreSQL и других БД.', 'mysql', 'DB', '2026-06-10 16:41:40.860167', true);
INSERT INTO public.sections (id, title, description, codename, "group", created_at, is_visible) VALUES ('ea498dac-c95d-4139-aacd-0c0dde534019', 'C/C++', 'Программирование на C и C++. Обсуждение компиляторов, управления памятью, многопоточности, шаблонов, CMake, отладки и оптимизации кода.', 'cpp', 'language', '2026-06-10 16:42:56.696253', true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users (id, username, email, password_hash, role, created_at, is_banned) VALUES ('9ff8a7d5-b47a-403a-a5f9-e85f1100f61b', 'admin', 'admin@codeforum.com', 'pbkdf2:sha256:600000$fMWeXxDfw9isL9R0$3594044d0a248418bc844e93b4bb1a47d0b857e4370f7dfa2680d8ea7397cf21', 'ADMIN', '2026-06-10 15:37:34.854629', false);
INSERT INTO public.users (id, username, email, password_hash, role, created_at, is_banned) VALUES ('bba5b37d-9c04-432d-ae00-41e233290f4e', 'usere', 'usere@gmail.com', 'pbkdf2:sha256:600000$3rbqEn4EHs0mrzyk$071795720e8a2a3e525d022ebf3123472da2c45233f684c56d0d2ba3f5320792', 'USER', '2026-06-10 16:27:07.574525', false);
INSERT INTO public.users (id, username, email, password_hash, role, created_at, is_banned) VALUES ('fdc73b8b-7079-4f12-9ecb-f91c3489b69e', 'pyfan', 'pyfan@gmail.com', 'pbkdf2:sha256:600000$rTXeDluXMraj6T4p$96dee2ef74bcd67ff642c4739cb2d3ac054ef35b8615c4f4195e34ef80c54da6', 'USER', '2026-06-10 16:52:00.275816', false);
INSERT INTO public.users (id, username, email, password_hash, role, created_at, is_banned) VALUES ('d7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'newbie', 'newbie@gmail.com', 'pbkdf2:sha256:600000$dgR31I0R42lQnLpU$d80c0d79fa32f113607c8c3f85741742adb2d168aaea0a412771f1a415b408cb', 'USER', '2026-06-10 17:14:06.561707', false);
INSERT INTO public.users (id, username, email, password_hash, role, created_at, is_banned) VALUES ('1cbff55a-b699-4d3e-b3de-798f37448777', 'moder', 'moder@codeforum.com', 'pbkdf2:sha256:600000$hsdmgzVIYucATegY$fc0f227c4d1fd2f26ed74d81c568069f8dcbd064becda91b64538cb210a1a7cc', 'MODERATOR', '2026-06-10 18:27:32.296817', false);
INSERT INTO public.users (id, username, email, password_hash, role, created_at, is_banned) VALUES ('d816fdb9-8bec-4998-8752-c08cd015cb70', 'pozornik', 'pozornik@codeforum.com', 'pbkdf2:sha256:600000$GVuNpL9SIM1O2uuc$dae93bf06fd984fe97d42d395cdf489122ba34b78dd50217d5dcdc9af1029617', 'USER', '2026-06-10 18:17:06.219896', true);


--
-- Data for Name: threads; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.threads (id, section_id, user_id, title, thread_type, views, created_at, is_pinned, is_closed) VALUES ('c7b91352-ad8b-41cc-a0d8-56cc10a63e63', 'b885b475-9af3-4048-a5d6-bb9788b9473d', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'ПОМОГИТИ!!', 'question', 0, '2026-06-10 17:26:03.470312', false, true);
INSERT INTO public.threads (id, section_id, user_id, title, thread_type, views, created_at, is_pinned, is_closed) VALUES ('103bcbf9-60ac-4ff1-beba-88cbc3f22ebb', 'ea498dac-c95d-4139-aacd-0c0dde534019', 'bba5b37d-9c04-432d-ae00-41e233290f4e', 'БАЗА ПО C++', 'resource', 0, '2026-06-10 17:59:19.780609', true, true);
INSERT INTO public.threads (id, section_id, user_id, title, thread_type, views, created_at, is_pinned, is_closed) VALUES ('16298f0c-82b3-4df1-a8d9-ff682fa2539b', 'ea498dac-c95d-4139-aacd-0c0dde534019', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'МОЙ ПРОЕКТ!!', 'showcase', 0, '2026-06-10 18:02:19.289745', false, false);
INSERT INTO public.threads (id, section_id, user_id, title, thread_type, views, created_at, is_pinned, is_closed) VALUES ('7c531c61-db40-45c1-bed0-69ca71b9ae3c', 'b885b475-9af3-4048-a5d6-bb9788b9473d', 'bba5b37d-9c04-432d-ae00-41e233290f4e', 'Flask vs Django', 'discussion', 0, '2026-06-10 16:50:23.118305', true, false);


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('de377039-cba3-4e3f-b1e8-a0765722bc72', '7c531c61-db40-45c1-bed0-69ca71b9ae3c', 'bba5b37d-9c04-432d-ae00-41e233290f4e', 'Всем привет!
Уже который год вижу в комментариях и на собеседованиях один и тот же вопрос: «Flask или Django?» Решил собрать здесь свой опыт и устроить честное обсуждение. Давайте разберём оба фреймворка без фанатизма.', '2026-06-10 16:50:23.167301', '2026-06-10 16:50:23.167301', false, '/uploads/attachments/921b49b8b2c64d9aa5907fb25eb0a50d__.png');
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('74cd93aa-308a-411e-bad8-45174816d15e', '7c531c61-db40-45c1-bed0-69ca71b9ae3c', 'fdc73b8b-7079-4f12-9ecb-f91c3489b69e', 'Be honest, сравнивать Flask и Django в 2026 году — это как сравнивать швейцарский нож и полноценный цех по обработке металла. Оба полезны, но для разных масштабов.

Как человек, который пишет на Django уже лет 10 и пережил все хайпы (включая «Flask-революцию» и «FastAPI-бум»), скажу прямо: для 95% веб-проектов **Django не имеет альтернатив**.
##Почему «гибкость» Flask — это ловушка
Ты пишешь, что Flask даёт гибкость. Да, это так. Но на практике эта «гибкость» превращается в decision fatigue (усталость от принятия решений).
Пока фласкер выбирает между Flask-Login, Flask-Security и самописным auth, настраивает CSRF-защиту, прикручивает Flask-Migrate и гуглит, как правильно организовать структуру папок (а ведь во Flask нет официального way!), джангист уже написал модель, сгенерировал миграции, создал суперюзера и зашёл в админку.
Django навязывает архитектуру (MTV), и это хорошо. Это спасает проекты от превращения в спагетти-код, когда в команду приходит новый разработчик.

Ты упомянул SQLAlchemy. Это мощная штука, но Django ORM для типовых задач (а веб — это на 90% типовые CRUD-операции) удобнее. А select_related и prefetch_related решают проблему N+1 на раз-два.
Но главное — Django Admin. Это вообще чит-код.
Ты делаешь модель -> регистрируешь в админке -> получаешь полноценный UI для управления контентом с фильтрами, поиском и правами доступа. Во Flask за это придётся платить кровью, потом и сторонними библиотеками, которые всё равно будут выглядеть как костыль.
##Безопасность из коробки
Flask по умолчанию небезопасен. Ты должен помнить, что нужно включить CSRF, помнить, как экранировать выводы, помнить про SQL-инъекции.
Django безопасен по умолчанию. CSRF-токены, защита от XSS, кликджекинга, SQL-инъекций — всё это работает сразу. Для коммерческого проекта в 2026 году это критично.', '2026-06-10 16:57:13.187986', '2026-06-10 16:59:44.600496', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('1075c61e-d828-43c0-bb43-4ce9a344a3eb', '7c531c61-db40-45c1-bed0-69ca71b9ae3c', '9ff8a7d5-b47a-403a-a5f9-e85f1100f61b', 'Flask lol. Сайт написан на нём лмао))', '2026-06-10 17:00:17.873968', '2026-06-10 17:00:17.873968', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('6f6e2c24-774d-4511-979d-b1f4ef6bb44e', 'c7b91352-ad8b-41cc-a0d8-56cc10a63e63', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'В вузе дали задание написать функции для факториала. Помогите :<', '2026-06-10 17:26:03.482301', '2026-06-10 17:26:03.482301', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('fd586a44-f229-477c-8a79-eda6f363dbf9', 'c7b91352-ad8b-41cc-a0d8-56cc10a63e63', 'fdc73b8b-7079-4f12-9ecb-f91c3489b69e', 'Ответ:

```python
#итеративная
def factorial(n: int):
    a = 1
    for i in range(1, n+1):
        a*=i
        return(a)

#рекурсивная
def f(n: int):
     # Базовый случай (условие выхода из рекурсии)
    if n == 0 or n == 1:
        return 1
    # Рекурсивный случай (функция вызывает саму себя)
    else:
        return n * factorial(n - 1)
```', '2026-06-10 17:29:26.278044', '2026-06-10 17:31:01.551919', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('284b4908-376a-49b4-b8db-0d04d51a6202', 'c7b91352-ad8b-41cc-a0d8-56cc10a63e63', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'Спасибо, pyfan!!', '2026-06-10 17:36:06.936188', '2026-06-10 17:36:06.936188', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('f6285ee9-15b3-4f46-882f-423fd182c458', '103bcbf9-60ac-4ff1-beba-88cbc3f22ebb', 'bba5b37d-9c04-432d-ae00-41e233290f4e', 'Статья must-read. Будьте вежливы, читайте книжки!!', '2026-06-10 17:59:19.784592', '2026-06-10 17:59:19.784592', false, '/uploads/attachments/feb3a1136d374d818fc0636e509ecb38_64512048aa944282bba07d47b77c672f_3786221723690266460b0b9690102761__1_C__C11-14-17-20_.pdf');
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('931a56a9-78e6-4e3c-b162-d4d006c80b48', '16298f0c-82b3-4df1-a8d9-ff682fa2539b', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'мой проект оцените!!', '2026-06-10 18:02:19.292744', '2026-06-10 18:02:19.292744', false, '/uploads/attachments/dab186bafc7840b39e31a2b02fcd31ed_-.zip');
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('1d6d4d61-c956-49c1-bac2-7854cfeafb8d', '16298f0c-82b3-4df1-a8d9-ff682fa2539b', '9ff8a7d5-b47a-403a-a5f9-e85f1100f61b', 'Кидайте ссылку на Github, пожалуйста!', '2026-06-10 18:03:23.293193', '2026-06-10 18:03:23.293193', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('fc3cdea3-05e1-41cb-87b2-f32c24aeaf43', '16298f0c-82b3-4df1-a8d9-ff682fa2539b', 'd816fdb9-8bec-4998-8752-c08cd015cb70', 'Трешня не знать про Github в 2k26. Понародили на курсах конечно', '2026-06-10 18:19:49.578843', '2026-06-10 18:19:49.578843', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('795e7c00-92e0-4005-b551-3a70689f75cd', '16298f0c-82b3-4df1-a8d9-ff682fa2539b', '1cbff55a-b699-4d3e-b3de-798f37448777', 'Пользователь pozornik заблокирован за токсичное поведение.
Обратитесь в поддержку!', '2026-06-10 18:31:24.042857', '2026-06-10 18:31:24.042857', false, NULL);
INSERT INTO public.posts (id, thread_id, user_id, content, created_at, updated_at, is_solution, attachment) VALUES ('74e2e592-efe6-4853-836c-419d12b11577', '7c531c61-db40-45c1-bed0-69ca71b9ae3c', 'bba5b37d-9c04-432d-ae00-41e233290f4e', '```Python
print("Hello world")
```', '2026-06-11 14:01:35.656749', '2026-06-11 14:01:35.656749', false, NULL);


--
-- Data for Name: ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('20ab1797-ca2f-4767-9e33-65a6c002aeed', '9ff8a7d5-b47a-403a-a5f9-e85f1100f61b', '74cd93aa-308a-411e-bad8-45174816d15e', '2026-06-10 17:07:16.87422');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('9e874ae6-1c4d-45ae-9d37-828701260cd8', 'bba5b37d-9c04-432d-ae00-41e233290f4e', '74cd93aa-308a-411e-bad8-45174816d15e', '2026-06-10 17:09:24.787424');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('bbbb7f3c-bdd8-4ba1-86ee-8c4afa25df0f', '9ff8a7d5-b47a-403a-a5f9-e85f1100f61b', 'fd586a44-f229-477c-8a79-eda6f363dbf9', '2026-06-10 17:35:04.981015');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('6c5e03a5-2375-46a5-b657-49d1a1acb7bf', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'fd586a44-f229-477c-8a79-eda6f363dbf9', '2026-06-10 17:36:11.323767');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('d90aae6b-fcc2-4351-90fa-57d4d4c3781b', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', 'de377039-cba3-4e3f-b1e8-a0765722bc72', '2026-06-10 17:44:19.476637');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('3edd9ebe-701f-4a07-b8d9-bf8b33fe996c', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', '74cd93aa-308a-411e-bad8-45174816d15e', '2026-06-10 17:44:32.16885');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('35476298-7373-44e0-86ad-c30bb24f7c40', 'd7126d7b-ffd6-443f-a5ed-f4b7ed27f5be', '6f6e2c24-774d-4511-979d-b1f4ef6bb44e', '2026-06-10 17:44:58.202634');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('0fe0d408-b884-49e5-9069-3483c88641b5', 'd816fdb9-8bec-4998-8752-c08cd015cb70', '74cd93aa-308a-411e-bad8-45174816d15e', '2026-06-10 18:17:33.166436');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('1a6f5e59-5674-4e55-9683-d3665ac6cb9c', 'd816fdb9-8bec-4998-8752-c08cd015cb70', 'fd586a44-f229-477c-8a79-eda6f363dbf9', '2026-06-10 18:17:51.095367');
INSERT INTO public.ratings (id, user_id, target_id, created_at) VALUES ('01787a6a-b84e-42c4-b9e5-0c05c22c291e', 'd816fdb9-8bec-4998-8752-c08cd015cb70', 'de377039-cba3-4e3f-b1e8-a0765722bc72', '2026-06-10 18:17:59.23389');


--
-- PostgreSQL database dump complete
--

\unrestrict ydCGHQrhGoClVghm8QDx6JuFIejeJVc81epGeJyvMmSDYndq1csWvf9LJZPVY8Z

