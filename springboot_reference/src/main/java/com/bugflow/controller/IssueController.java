package com.bugflow.controller;

import com.bugflow.entity.IndividualBugSaga;
import com.bugflow.service.IssueService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/bugs")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class IssueController {

    private final IssueService issueService;

    @GetMapping
    public ResponseEntity<List<IndividualBugSaga>> listBugs() {
        return ResponseEntity.ok(issueService.getAllIssues());
    }

    @GetMapping("/{id}")
    public ResponseEntity<IndividualBugSaga> getBug(@PathVariable Long id) {
        return ResponseEntity.ok(issueService.getIssueById(id));
    }

    @PostMapping("/{id}/transition")
    public ResponseEntity<IndividualBugSaga> transitionBug(
            @PathVariable Long id,
            @RequestParam String targetStage,
            @RequestParam(required = false, defaultValue = "") String note) {
        return ResponseEntity.ok(issueService.transitionStage(id, targetStage, note));
    }
}
