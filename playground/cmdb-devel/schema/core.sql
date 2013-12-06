-- Core SQL schema for application-dependency prototype.

create table object_type (
    id
,   name
,   description
)

create table object_type_attribute (
    id
,   object_type_id
,   attribute_name
,   attribute_type
)

create table relationship_type (
    id
,   source_object_type_id
,   target_object_type_id
,   source_target_relationship
,   target_source_relationship
,   arity
)

create table object (
    id
,   object_type_id
,   object_name
)

create table object_attribute
(
    id
,   object_id
,   object_attribute_id
,   value
--  order ?
)

create table object_relationship
(
    id
,   source_object_id
,   target_object_id
)
