INSERT INTO svcmodel.val_selector_node_type 
    (selector_node_type, min_children, max_children)
	    VALUES ('intersection', 1, NULL);

INSERT INTO svcmodel.val_selector_node_type 
    (selector_node_type, min_children, max_children)
	    VALUES ('union', 1, NULL);

INSERT INTO svcmodel.val_selector_node_type
    (selector_node_type, min_children, max_children)
	    VALUES ('null', 0, 1);

INSERT INTO svcmodel.val_selector_node_type
    (selector_node_type, min_children, max_children)
	    VALUES ('expression', 0, 0);
