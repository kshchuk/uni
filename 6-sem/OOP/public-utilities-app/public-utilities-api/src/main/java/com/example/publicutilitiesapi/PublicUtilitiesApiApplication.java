package com.example.publicutilitiesapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication(scanBasePackages = "com.example.publicutilitiesapi.*")
@EnableJpaRepositories("com.example.publicutilitiesapi.repository")
public class PublicUtilitiesApiApplication {

	public static void main(String[] args) {
		SpringApplication.run(PublicUtilitiesApiApplication.class, args);
	}

}
