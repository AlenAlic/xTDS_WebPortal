{#- Define the different disciplines of the tournament. -#}
{%- set discipline_Ballroom = 1 -%}
{%- set discipline_Latin = 2 -%}
{%- set discipline_Salsa = 3 -%}
{%- set discipline_Polka = 4 -%}
{#- Define the different classes of the tournament. -#}
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
{#- Define the different dances with id, name, tag (short name) and disc (which discipline it belongs to, pointer) -#}
{%- set dance_SW = 1 -%}
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
{#- Define the different tournaments, normally every discipline-class combination has its own tournament. -#}
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
{#- Set the id of the organization team. -#}
{%- set team_organization = 100 -%}