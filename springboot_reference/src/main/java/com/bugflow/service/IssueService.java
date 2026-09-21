package com.bugflow.service;

import com.bugflow.entity.IndividualBugSaga;
import com.bugflow.repository.IssueRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class IssueService {

    private final IssueRepository issueRepository;

    public List<IndividualBugSaga> getAllIssues() {
        return issueRepository.findAll();
    }

    public IndividualBugSaga getIssueById(Long id) {
        return issueRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Issue not found with id: " + id));
    }

    @Transactional
    public IndividualBugSaga transitionStage(Long id, String targetStage, String note) {
        IndividualBugSaga issue = getIssueById(id);
        issue.setDevStage(targetStage);
        if ("CLOSED".equalsIgnoreCase(targetStage)) {
            issue.setClosedAt(LocalDateTime.now());
        }
        return issueRepository.save(issue);
    }
}
