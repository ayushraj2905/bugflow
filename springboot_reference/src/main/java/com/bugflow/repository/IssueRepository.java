package com.bugflow.repository;

import com.bugflow.entity.IndividualBugSaga;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface IssueRepository extends JpaRepository<IndividualBugSaga, Long> {
    Optional<IndividualBugSaga> findByIssueKey(String issueKey);
    List<IndividualBugSaga> findByDevStage(String devStage);
    List<IndividualBugSaga> findByProjectId(Long projectId);
    List<IndividualBugSaga> findByAssigneeId(Long assigneeId);
}
