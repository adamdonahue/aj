-- Open questions:
--   Where do versions fit in?
--     Two types of version:
--        Record versions, i.e., changes to a database entry.
--        CI versions, proper changes
--   

-- HDP

--
-- Hierarchical representation of class categories.
-- Open question: is there a difference between classes and categories;
-- i.e. are there cross-cutting concerns where a category and its child
-- would not map to a class hierarchy isomorphically?
--

-- create table cm_namespace
-- (
--     namespace varchar(128) not null
-- ,   description varchar(256)
-- ,   primary key (namespace)
-- )
-- /

-- create table ci_class_category 
-- (
--     ci_class_category_id serial not null
-- ,   ci_class_category_name varchar(256) not null
-- ,   ci_class_category_description
-- 
-- )

-- The types of things that will be included, in ITILv3 known
-- as the scope.
--
-- See also:
--   Desktop Management Task Force (DMTF)'s Common Information Model (CIM)
--
create table ci_class
(
    ci_class_id  serial       not null
,   name         varchar(128) not null
,   namespace    varchar(128) not null
,   primary key (ci_class_id)
,   unique (namespace, name)
)
/

create table ci_class_hierarchy
(
    ci_class_id integer not null
,   ci_class_parent_id integer not null
,   primary key (ci_class_id, ci_class_parent_id)
,   foreign key (ci_class_parent_id) references ci_class (ci_class_id)
)
/

create table ci_class_attribute
(
    ci_class_attribute_id serial       not null
,   attribute_name        varchar(128) not null
,   attribute_type        varchar(128) not null         -- str, int, object, fn, etc.
,   required              boolean      not null default false
,   propagate             boolean      not null default true -- do we propagate attributes to children?
)
/

create table r_class 
(
    r_class_id                 serial       not null
,   source_ci_class_id         integer      not null
,   target_ci_class_id         integer      not null
,   source_to_target_semantics varchar(128) not null
,   target_to_source_semantics varchar(128) not null
,   cardinality                varchar(8)   not null -- 1-n, n-n, n-1 ...   
)
/

create table r_class_attribute
(
    r_class_attribute_id serial       not null
,   r_class_id           integer      not null
,   attribute_name       varchar(128) not null
,   attribute_type       varchar(128) not null
,   required             boolean      not null default false
)
/

create table ci
(
    ci_id       serial       not null
,   ci_class_id integer      not null 
,   ci_name     varchar(128) not null   -- this might just be an attribute
,   primary key (ci_id)
)
/

-- Here we run into the annoying limitations of RDBMS for
-- modeling hierarchical data structures.
--
-- That is, we want to allow a class to have the attribute
-- if the class -or any of its ancestors- support the attribute.
--
-- This is easy to model if we use first-order tables to
-- represent classes.  But here we're doing second-order
-- modeling: representing entities as rows as well as instances.
--

create table r
(
    r_id         serial  not null
,   r_class_id   integer not null
,   source_ci_id integer not null
,   target_ci_id integer not null
--  check that the cardinality is correct
--  check that the source and target match the r_class
)
/

create table ci_attribute
(
    ci_id                 integer      not null,
,   ci_class_attribute_id integer      not null
,   attribute_value       varchar(128) not null     -- As an example; will need more representations.
--  check that the ci is a member of a class that has that attribute, 
--  either directly or via an ancestor
)
/

create table r_attribute
(
    r_id                 integer      not null
,   r_class_attribute_id integer      not null
,   attribute_value      varchar(128) not null
--  checks
)
/
