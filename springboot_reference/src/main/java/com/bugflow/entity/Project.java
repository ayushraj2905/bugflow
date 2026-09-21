package com.bugflow.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "projects")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Project {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_id")
    private Long id;

    @Column(name = "project_name", nullable = false)
    private String projectName;

    @Column(nullable = false)
    private String codebase;

    @Column(name = "development_cycle")
    private String developmentCycle;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
