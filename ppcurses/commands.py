def add_comment(card, value):
    pass


def edit_title(card, value):
    pass


def edit_description(card, value):
    pass


def edit_assignee(card, value):
    pass


def add_contributor(card, value):
    pass


def remove_contributor(card, value):
    pass


def edit_label(card, value):
    pass


def edit_points(card, value):
    pass


def add_tag(card, value):
    pass


def remove_tag(card, value):
    pass


def toggle_checklist_item(card, value):
    pass


def add_checklist_item(card, value):
    pass


def edit_checklist_item(card, value):
    pass


def remove_checklist_item(card, value):
    pass


def like_comment(self):
    pass


def remove_comment(self):
    pass


mappings = {
    'an': add_comment,
    'et': edit_title,
    'ed': edit_description,
    'ea': edit_assignee,
    'ac': add_contributor,
    'xc': remove_contributor,
    'el': edit_label,
    'ep': edit_points,
    'at': add_tag,
    'xt': remove_tag,
    'tl<num:int>': toggle_checklist_item,
    'al': add_checklist_item,
    'et<num:int>': edit_checklist_item,
    'xt<num:int>': remove_checklist_item,
    'ln<num:int>': like_comment,
    'xn<num:int>': remove_comment,
}
