drop table if exists user;
create table user (
	user_id integer primary key autoincrement,
	username text not null,
	email text not null,
	pw_hash text not null
);

drop table if exists article;
create table article (
	article_id integer primary key autoincrement,
	author_id integer not null,
	url text not null,
	post_date integer,
	thumb_file_path text
);