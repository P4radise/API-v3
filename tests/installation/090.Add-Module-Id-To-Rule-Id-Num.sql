declare
    c_before_module_start_rule_type_id constant rule_type.rule_type_id%type := 120;
    v_module_id module.module_id%type;
    cursor cur_module_rules_by_comp_package(p_comp_package in components_package.name%type) is
        select rule.rule_id, rule.rule
          from rule
          join rule_type rt on rt.rule_type_id = rule.rule_type_id
                           and rule.rule_type_id in (c_before_module_start_rule_type_id)
          join comp_pkg_object_xref cpx on cpx.object_id = rule.rule_id
                                       and cpx.component_id = pkg_audit_comp.c_rule_component_id
          join components_package cp on cp.components_package_id = cpx.components_package_id
                                    and cp.name = p_comp_package;
begin
    select max(module_id)
      into v_module_id
      from module
     where git_repo_url = 'https://github.com/ov-integrations/ov-python-api-samples';

    for rec_rule in cur_module_rules_by_comp_package('VHMPYAPI') loop
        dbms_output.put_line('Adding a Module ID to the ID num for a rule [' ||  rec_rule.rule || ']' || pkg_str.c_lb);

        insert into rule_id_num(rule_id, id_num) 
        values(rec_rule.rule_id, v_module_id);

        commit;
    end loop;
end;