package com.bugflow.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "individual_bug_saga")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class IndividualBugSaga {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "saga_id")
    private Long id;

    @Column(name = "issue_key", unique = true, nullable = false)
    private String issueKey;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private BugCategory category;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String description;

    @Column(name = "reproduction_steps", columnDefinition = "TEXT")
    private String reproductionSteps;

    @Column(name = "affected_module")
    private String affectedModule;

    @Column(name = "environment_info")
    private String environmentInfo;

    private String severity; // CRITICAL, MAJOR, MINOR, LOW
    private String priority; // P1, P2, P3, P4

    @Column(name = "dev_stage")
    private String devStage; // REPORTED, TRIAGED, ASSIGNED, IN_PROGRESS, CODE_REVIEW, QA_TESTING, CLOSED

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reporter_id")
    private UserDevProfile reporter;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assignee_id")
    private UserDevProfile assignee;

    @Column(name = "estimated_effort")
    private Double estimatedEffort;

    @Column(name = "actual_effort")
    private Double actualEffort;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "closed_at")
    private LocalDateTime closedAt;
}
