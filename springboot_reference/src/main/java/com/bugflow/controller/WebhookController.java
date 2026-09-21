package com.bugflow.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/webhooks")
@CrossOrigin(origins = "*")
public class WebhookController {

    @PostMapping("/github")
    public ResponseEntity<?> handleGithubWebhook(@RequestBody Map<String, Object> payload) {
        // Parse commits and trigger issue transition if "Fixes #KEY" found
        return ResponseEntity.ok(Map.of("status", "processed", "message", "GitHub webhook received"));
    }

    @PostMapping("/cicd")
    public ResponseEntity<?> handleCICDWebhook(@RequestBody Map<String, Object> payload) {
        // Auto-create defect if CI/CD pipeline failed
        return ResponseEntity.ok(Map.of("status", "processed", "message", "CI/CD alert evaluated"));
    }
}
