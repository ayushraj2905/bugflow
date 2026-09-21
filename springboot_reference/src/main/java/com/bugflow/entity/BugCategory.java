package com.bugflow.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "bug_categories")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BugCategory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "category_id")
    private Long id;

    @Column(name = "category_name", nullable = false)
    private String categoryName;

    @Column(name = "urgency_enum", nullable = false)
    private String urgencyEnum;
}
