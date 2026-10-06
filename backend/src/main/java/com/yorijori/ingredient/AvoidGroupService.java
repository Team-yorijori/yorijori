package com.yorijori.ingredient;

import com.yorijori.ingredient.dto.AvoidGroupResponse;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class AvoidGroupService {

    private final AvoidGroupRepository groups;

    public AvoidGroupService(AvoidGroupRepository groups) {
        this.groups = groups;
    }

    public List<AvoidGroupResponse> list() {
        return groups.findAllByOrderBySortNoAsc().stream().map(AvoidGroupResponse::of).toList();
    }

    public Set<String> groupNames() {
        return groups.findAll().stream().map(AvoidGroup::getName).collect(Collectors.toCollection(LinkedHashSet::new));
    }

    public List<String> termsOf(String groupName) {
        return groups.findByName(groupName).map(g -> List.copyOf(g.getTerms())).orElse(List.of());
    }
}
