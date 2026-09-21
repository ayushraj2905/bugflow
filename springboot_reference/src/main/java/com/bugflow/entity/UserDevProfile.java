package com.bugflow.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_dev_profiles")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserDevProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "dev_id")
    private Long id;

    @Column(name = "full_name", nullable = false)
    private String fullName;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String team;

    @Column(name = "core_skills", nullable = false)
    private String coreSkills;

    @Column(nullable = false)
    private String proficiency; // Junior, Mid, Senior, Lead

    @Column(nullable = false)
    private String role; // ADMIN, PROJECT_MANAGER, DEVELOPER, QA_TESTER, REPORTER

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
