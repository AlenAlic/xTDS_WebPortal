USE `BADdb`;

-- Define the event itself
INSERT INTO `event` SET `id` = 1, `name` = 'ETDS 2018 Brno';

-- Define the different disciplines
{% set discipline_Ballroom = 1 -%}
{%- set discipline_Latin = 2 -%}
{%- set discipline_Salsa = 3 -%}
{%- set discipline_Polka = 4 -%}
INSERT INTO `discipline` SET `id` = {{discipline_Ballroom}}, `name` = 'Ballroom';
INSERT INTO `discipline` SET `id` = {{discipline_Latin}}, `name` = 'Latin';
INSERT INTO `discipline` SET `id` = {{discipline_Salsa}}, `name` = 'Salsa';
INSERT INTO `discipline` SET `id` = {{discipline_Polka}}, `name` = 'Polka';

-- Define the different classes
{% set class_Breitensport_qualification = 1 -%}
{%- set class_Breitensport_Amateurs = 2 -%}
{%- set class_Breitensport_Professionals = 3 -%}
{%- set class_Breitensport_Masters = 4 -%}
{%- set class_Breitensport_Champions = 5 -%}
{%- set class_CloseD = 10 -%}
{%- set class_Open_Class = 20 -%}
{%- set class_Salsa = 30 -%}
{%- set class_Polka = 40 -%}
{%- set class_TEST = 99 -%}
INSERT INTO `class` SET `id` = {{class_Breitensport_qualification}}, `name` = 'Breitensport (Qualification)';
INSERT INTO `class` SET `id` = {{class_Breitensport_Amateurs}}, `name` = 'Amateurs';
INSERT INTO `class` SET `id` = {{class_Breitensport_Professionals}}, `name` = 'Profis';
INSERT INTO `class` SET `id` = {{class_Breitensport_Masters}}, `name` = 'Masters';
INSERT INTO `class` SET `id` = {{class_Breitensport_Champions}}, `name` = 'Champions';
INSERT INTO `class` SET `id` = {{class_CloseD}}, `name` = 'CloseD';
INSERT INTO `class` SET `id` = {{class_Open_Class}}, `name` = 'Open Class';
INSERT INTO `class` SET `id` = {{class_Salsa}}, `name` = 'Salsa';
INSERT INTO `class` SET `id` = {{class_Polka}}, `name` = 'Polka';
INSERT INTO `class` SET `id` = {{class_TEST}}, `name` = 'TEST';

-- Define the different dances with id, name, tag (short name) and disc (which discipline it belongs to, pointer)
{% set dance_SW = 1 -%}
{%- set dance_TG = 2 -%}
{%- set dance_VW = 3 -%}
{%- set dance_SF = 4 -%}
{%- set dance_QS = 5 -%}
{%- set dance_SB = 6 -%}
{%- set dance_CC = 7 -%}
{%- set dance_RB = 8 -%}
{%- set dance_PD = 9 -%}
{%- set dance_JV = 10 -%}
{%- set dance_SS = 20 -%}
{%- set dance_BC = 21 -%}
{%- set dance_MG = 22 -%}
{%- set dance_PK = 30 -%}
INSERT INTO `dance` SET `id` = {{dance_SW}}, `name` = 'Slow Waltz', `tag` = 'SW', `disc` = {{discipline_Ballroom}};
INSERT INTO `dance` SET `id` = {{dance_TG}}, `name` = 'Tango', `tag` = 'TG', `disc` = {{discipline_Ballroom}};
INSERT INTO `dance` SET `id` = {{dance_VW}}, `name` = 'Viennese Waltz', `tag` = 'VW', `disc` = {{discipline_Ballroom}};
INSERT INTO `dance` SET `id` = {{dance_SF}}, `name` = 'Slow Foxtrot', `tag` = 'SF', `disc` = {{discipline_Ballroom}};
INSERT INTO `dance` SET `id` = {{dance_QS}}, `name` = 'Quickstep', `tag` = 'QS', `disc` = {{discipline_Ballroom}};
INSERT INTO `dance` SET `id` = {{dance_SB}}, `name` = 'Samba', `tag` = 'SB', `disc` = {{discipline_Latin}};
INSERT INTO `dance` SET `id` = {{dance_CC}}, `name` = 'Cha Cha', `tag` = 'CC', `disc` = {{discipline_Latin}};
INSERT INTO `dance` SET `id` = {{dance_RB}}, `name` = 'Rumba', `tag` = 'RB', `disc` = {{discipline_Latin}};
INSERT INTO `dance` SET `id` = {{dance_PD}}, `name` = 'Paso Doble', `tag` = 'PD', `disc` = {{discipline_Latin}};
INSERT INTO `dance` SET `id` = {{dance_JV}}, `name` = 'Jive', `tag` = 'JV', `disc` = {{discipline_Latin}};
INSERT INTO `dance` SET `id` = {{dance_SS}}, `name` = 'Salsa', `tag` = 'SS', `disc` = {{discipline_Salsa}};
INSERT INTO `dance` SET `id` = {{dance_BC}}, `name` = 'Bachata', `tag` = 'BC', `disc` = {{discipline_Salsa}};
INSERT INTO `dance` SET `id` = {{dance_MG}}, `name` = 'Merengue', `tag` = 'MG', `disc` = {{discipline_Salsa}};
INSERT INTO `dance` SET `id` = {{dance_PK}}, `name` = 'Polka', `tag` = 'PK', `disc` = {{discipline_Polka}};

-- Define the different tournaments, normally every discipline-class combination has its own tournament.
-- Mode SP: since our couples will remain fixed during each tournament
-- May link to its qualification tournament, in which case no new starting numbers are needed
{% set tournament_Ballroom_Breitensport_qualification = 1 -%}
{%- set tournament_Ballroom_Breitensport_Amateurs = 2 -%}
{%- set tournament_Ballroom_Breitensport_Professionals = 3 -%}
{%- set tournament_Ballroom_Breitensport_Masters = 4 -%}
{%- set tournament_Ballroom_Breitensport_Champions = 5 -%}
{%- set tournament_Ballroom_CloseD = 20 -%}
{%- set tournament_Ballroom_Open_Class = 30 -%}
{%- set tournament_Salsa = 40 -%}
{%- set tournament_Latin_Breitensport_qualification = 11 -%}
{%- set tournament_Latin_Breitensport_Amateurs = 12 -%}
{%- set tournament_Latin_Breitensport_Professionals = 13 -%}
{%- set tournament_Latin_Breitensport_Masters = 14 -%}
{%- set tournament_Latin_Breitensport_Champions = 15 -%}
{%- set tournament_Latin_CloseD = 21 -%}
{%- set tournament_Latin_Open_Class = 31 -%}
{%- set tournament_Polka = 50 -%}
{%- set tournament_TEST = 99 -%}
-- Day 1
INSERT INTO `tournament` SET `id` = {{tournament_Ballroom_Breitensport_qualification}}, `event` = 1, `class` = {{class_Breitensport_qualification}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-03 09:00', `mode` = 'SP', `numberl0` = 1, `numberl1` = 199;
INSERT INTO `tournament` SET `id` = {{tournament_Ballroom_Breitensport_Amateurs}}, `event` = 1, `class` = {{class_Breitensport_Amateurs}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-03 11:00', `mode` = 'SP', `quali` = {{tournament_Ballroom_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Ballroom_Breitensport_Professionals}}, `event` = 1, `class` = {{class_Breitensport_Professionals}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-03 12:00', `mode` = 'SP', `quali` = {{tournament_Ballroom_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Ballroom_Breitensport_Masters}}, `event` = 1, `class` = {{class_Breitensport_Masters}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-03 13:00', `mode` = 'SP', `quali` = {{tournament_Ballroom_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Ballroom_Breitensport_Champions}}, `event` = 1, `class` = {{class_Breitensport_Champions}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-03 14:00', `mode` = 'SP', `quali` = {{tournament_Ballroom_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Latin_CloseD}}, `event` = 1, `class` = {{class_CloseD}}, `disc` = {{discipline_Latin}}, `when` = '2018-03-03 15:00', `mode` = 'CP_D', `numberl0` = 200, `numberl1` = 299;
INSERT INTO `tournament` SET `id` = {{tournament_Latin_CloseD}}, `event` = 1, `class` = {{class_Open_Class}}, `disc` = {{discipline_Latin}}, `when` = '2018-03-03 15:00', `mode` = 'CP_D', `numberl0` = 300, `numberl1` = 399;
INSERT INTO `tournament` SET `id` = {{tournament_Salsa}}, `event` = 1, `class` = {{class_Salsa}}, `disc` = {{discipline_Salsa}}, `when` = '2018-03-03 15:00', `mode` = 'CP_D', `numberl0` = 400, `numberl1` = 599;
-- Day 2
INSERT INTO `tournament` SET `id` = {{tournament_Latin_Breitensport_qualification}}, `event` = 1, `class` = {{class_Breitensport_qualification}}, `disc` = {{discipline_Latin}}, `when` = '2018-03-04 09:00', `mode` = 'SP', `numberl0` = 1, `numberl1` = 199;
INSERT INTO `tournament` SET `id` = {{tournament_Latin_Breitensport_Amateurs}}, `event` = 1, `class` = {{class_Breitensport_Amateurs}}, `disc` = {{discipline_Latin}}, `when` = '2018-03-04 11:00', `mode` = 'SP', `quali` = {{tournament_Latin_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Latin_Breitensport_Professionals}}, `event` = 1, `class` = {{class_Breitensport_Professionals}}, `disc` = {{discipline_Latin}}, `when` = '2018-03-04 12:00', `mode` = 'SP', `quali` = {{tournament_Latin_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Latin_Breitensport_Masters}}, `event` = 1, `class` = {{class_Breitensport_Masters}}, `disc` = {{discipline_Latin}}, `when` = '2018-03-04 13:00', `mode` = 'SP', `quali` = {{tournament_Latin_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Latin_Breitensport_Champions}}, `event` = 1, `class` = {{class_Breitensport_Champions}}, `disc` = {{discipline_Latin}}, `when` = '2018-03-04 14:00', `mode` = 'SP', `quali` = {{tournament_Latin_Breitensport_qualification}};
INSERT INTO `tournament` SET `id` = {{tournament_Latin_CloseD}}, `event` = 1, `class` = {{class_CloseD}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-04 15:00', `mode` = 'CP_D', `numberl0` = 200, `numberl1` = 299;
INSERT INTO `tournament` SET `id` = {{tournament_Latin_Open_Class}}, `event` = 1, `class` = {{class_Open_Class}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-04 15:00', `mode` = 'CP_D', `numberl0` = 300, `numberl1` = 399;
INSERT INTO `tournament` SET `id` = {{tournament_Polka}}, `event` = 1, `class` = {{class_Polka}}, `disc` = {{discipline_Polka}}, `when` = '2018-03-03 15:00', `mode` = 'SP', `numberl0` = 400, `numberl1` = 599;
-- Test to educate judges
INSERT INTO `tournament` SET `id` = {{tournament_TEST}}, `event` = 1, `class` = {{class_TEST}}, `disc` = {{discipline_Ballroom}}, `when` = '2018-03-03 08:00', `mode` = 'SP', `numberl0` = 900, `numberl1` = 999;

-- The dances to be danced in tournament, altered in webUI prior to actual rounds
-- First day
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_qualification}}, `dance` = {{dance_SW}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_qualification}}, `dance` = {{dance_TG}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_qualification}}, `dance` = {{dance_QS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Amateurs}}, `dance` = {{dance_SW}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Amateurs}}, `dance` = {{dance_TG}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Amateurs}}, `dance` = {{dance_QS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Professionals}}, `dance` = {{dance_SW}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Professionals}}, `dance` = {{dance_TG}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Professionals}}, `dance` = {{dance_QS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Masters}}, `dance` = {{dance_SW}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Masters}}, `dance` = {{dance_TG}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Masters}}, `dance` = {{dance_QS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Champions}}, `dance` = {{dance_SW}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Champions}}, `dance` = {{dance_TG}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Champions}}, `dance` = {{dance_QS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_CloseD}}, `dance` = {{dance_SW}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_CloseD}}, `dance` = {{dance_TG}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_CloseD}}, `dance` = {{dance_QS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Open_Class}}, `dance` = {{dance_SB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Open_Class}}, `dance` = {{dance_CC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Open_Class}}, `dance` = {{dance_RB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Open_Class}}, `dance` = {{dance_PD}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Open_Class}}, `dance` = {{dance_JV}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Salsa}}, `dance` = {{dance_SS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Salsa}}, `dance` = {{dance_BC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Salsa}}, `dance` = {{dance_MG}};
-- Second day
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_qualification}}, `dance` = {{dance_CC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_qualification}}, `dance` = {{dance_RB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_qualification}}, `dance` = {{dance_JV}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Amateurs}}, `dance` = {{dance_CC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Amateurs}}, `dance` = {{dance_RB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Amateurs}}, `dance` = {{dance_JV}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Professionals}}, `dance` = {{dance_CC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Professionals}}, `dance` = {{dance_RB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Professionals}}, `dance` = {{dance_JV}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Masters}}, `dance` = {{dance_CC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Masters}}, `dance` = {{dance_RB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Masters}}, `dance` = {{dance_JV}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Champions}}, `dance` = {{dance_CC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Champions}}, `dance` = {{dance_RB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Latin_Breitensport_Champions}}, `dance` = {{dance_JV}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_CloseD}}, `dance` = {{dance_SW}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_CloseD}}, `dance` = {{dance_TG}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_CloseD}}, `dance` = {{dance_QS}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Open_Class}}, `dance` = {{dance_SB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Open_Class}}, `dance` = {{dance_CC}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Open_Class}}, `dance` = {{dance_RB}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Open_Class}}, `dance` = {{dance_PD}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Ballroom_Breitensport_Open_Class}}, `dance` = {{dance_JV}};
INSERT INTO `t_dance` SET `tourn` = {{tournament_Polka}}, `dance` = {{dance_PK}};

-- Teams
-- Define the different teams competing in tournament
INSERT INTO `team` SET `id` = 100, `name` = 'ORGANIZATION';
{%- for team in teams %}
INSERT INTO `team` SET `id` = {{ team.team_id }}, `name` = '{{ team.name }} ({{team.city}})';
{%- endfor %}

-- BAD team person files
INSERT INTO `person` SET `id` = 1000, `fname` = 'Root', `name` = 'Admin', `team` = 100;
INSERT INTO `person` SET `id` = 1001, `fname` = 'BAD', `name` = 'manager', `team` = 100;
INSERT INTO `person` SET `id` = 1002, `fname` = 'BAD', `name` = 'assistant', `team` = 100;
INSERT INTO `person` SET `id` = 1003, `fname` = 'Floor1', `name` = 'Manager', `team` = 100;
INSERT INTO `person` SET `id` = 1004, `fname` = 'Floor2', `name` = 'Manager', `team` = 100;
INSERT INTO `person` SET `id` = 1005, `fname` = 'Floor3', `name` = 'Manager', `team` = 100;

-- BAD team login codes
INSERT INTO `staff` SET `id` = 1000, `tag` = 'rt', `password` = SHA1('root');
INSERT INTO `staff` SET `id` = 1001, `tag` = 'BADm', `password` = SHA1('ntds');
INSERT INTO `staff` SET `id` = 1002, `tag` = 'BADa', `password` = SHA1('ntds');
INSERT INTO `staff` SET `id` = 1003, `tag` = 'F1', `password` = SHA1('floor');
INSERT INTO `staff` SET `id` = 1004, `tag` = 'F2', `password` = SHA1('floor');
INSERT INTO `staff` SET `id` = 1005, `tag` = 'F3', `password` = SHA1('floor');

-- BAD team jobs
INSERT INTO `employ` SET `role` = 'admin' , `who` = 1000;
INSERT INTO `employ` SET `role` = 'admin' , `who` = 1001;
INSERT INTO `employ` SET `role` = 'admin' , `who` = 1002;
INSERT INTO `employ` SET `role` = 'support' , `who` = 1003;
INSERT INTO `employ` SET `role` = 'support' , `who` = 1004;
INSERT INTO `employ` SET `role` = 'support' , `who` = 1005;

-- TEST Lead and Follows
INSERT INTO `person` SET `id` = 9001, `fname` = 'Leader1', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9002, `fname` = 'Leader2', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9003, `fname` = 'Follower1', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9004, `fname` = 'Follower2', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9005, `fname` = 'Leader3', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9006, `fname` = 'Leader4', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9007, `fname` = 'Follower3', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9008, `fname` = 'Follower4', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9009, `fname` = 'Leader5', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9010, `fname` = 'Leader6', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9011, `fname` = 'Follower5', `name` = 'Test', `team` = 100;
INSERT INTO `person` SET `id` = 9012, `fname` = 'Follower6', `name` = 'Test', `team` = 100;

SHOW WARNINGS;