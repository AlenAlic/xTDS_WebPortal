-- {% extends "organizer/_BAD_variables.sql" %}
USE `BADdb`;

-- Define the event itself
INSERT INTO `event` SET `id` = 1, `name` = 'ETDS 2018 Brno';

-- Define the different teams competing in tournament
-- Organization team
{% set team_organization = 100 -%}
INSERT INTO `team` SET `id` = {{ team_organization }}, `name` = 'ORGANIZATION';
-- Other teams
{%- for team in teams %}
INSERT INTO `team` SET `id` = {{ team.team_id }}, `name` = '{{ team.name }} ({{team.city}})';
{%- endfor %}

-- BAD team
-- Users
INSERT INTO `person` SET `id` = 1000, `fname` = 'Root', `name` = 'Admin', `team` = {{ team_organization }};
INSERT INTO `person` SET `id` = 1001, `fname` = 'BAD', `name` = 'manager', `team` = {{ team_organization }};
INSERT INTO `person` SET `id` = 1002, `fname` = 'BAD', `name` = 'assistant', `team` = {{ team_organization }};
INSERT INTO `person` SET `id` = 1003, `fname` = 'Floor1', `name` = 'Manager', `team` = {{ team_organization }};
INSERT INTO `person` SET `id` = 1004, `fname` = 'Floor2', `name` = 'Manager', `team` = {{ team_organization }};
INSERT INTO `person` SET `id` = 1005, `fname` = 'Floor3', `name` = 'Manager', `team` = {{ team_organization }};
-- User login codes
INSERT INTO `staff` SET `id` = 1000, `tag` = 'rt', `password` = SHA1('root');
INSERT INTO `staff` SET `id` = 1001, `tag` = 'BADm', `password` = SHA1('etds');
INSERT INTO `staff` SET `id` = 1002, `tag` = 'BADa', `password` = SHA1('etds');
INSERT INTO `staff` SET `id` = 1003, `tag` = 'F1', `password` = SHA1('floor');
INSERT INTO `staff` SET `id` = 1004, `tag` = 'F2', `password` = SHA1('floor');
INSERT INTO `staff` SET `id` = 1005, `tag` = 'F3', `password` = SHA1('floor');
-- User jobs
INSERT INTO `employ` SET `role` = 'admin' , `who` = 1000;
INSERT INTO `employ` SET `role` = 'admin' , `who` = 1001;
INSERT INTO `employ` SET `role` = 'admin' , `who` = 1002;
INSERT INTO `employ` SET `role` = 'support' , `who` = 1003;
INSERT INTO `employ` SET `role` = 'support' , `who` = 1004;
INSERT INTO `employ` SET `role` = 'support' , `who` = 1005;

SHOW WARNINGS;