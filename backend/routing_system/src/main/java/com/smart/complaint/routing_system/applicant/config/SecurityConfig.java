package com.smart.complaint.routing_system.applicant.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order; // ★ 순서 정하기용
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityCustomizer; // ★ 스웨거용
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    // 비밀번호 암호화 도구
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // Swagger 등 정적 리소스는 보안 필터 아예 거치지 않게 무시 (500 에러 해결)
    @Bean
    public WebSecurityCustomizer webSecurityCustomizer() {
        return (web) -> web.ignoring()
                .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html");
    }

    // 공무원 전용 (세션 방식)
    @Bean
    @Order(1)
    public SecurityFilterChain agentFilterChain(HttpSecurity http) throws Exception {
        http
                .securityMatcher("/api/agent/**") // ★ 이 주소만 담당
                .csrf(csrf -> csrf.disable())     // 개발 편의상 일단 끔 (나중에 켜도 됨)
                .cors(cors -> cors.configure(http))

                // ★ 핵심: 공무원은 세션(Session)을 쓴다!
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED) // 필요하면 세션 생성
                )

                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/agent/login").permitAll() // 로그인은 누구나 접속 가능
                        .anyRequest().authenticated() // 그 외 공무원 기능은 로그인 필수
                );

        return http.build();
    }

    // 시민/공용 (JWT 방식) - 나머지 전부 담당
    @Bean
    @Order(2)
    public SecurityFilterChain publicFilterChain(HttpSecurity http) throws Exception {
        http
                .securityMatcher("/api/auth/**", "/api/complaint/**", "/api/**") // 나머지 API들
                .csrf(csrf -> csrf.disable())
                .cors(cors -> cors.configure(http))

                // 시민은 세션을 안 쓴다 (Stateless) ->  JWT 필터 들어갈 곳
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                )

                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/auth/**").permitAll() // 시민 로그인/회원가입 허용
                        // .anyRequest().authenticated() // 원래는 막아야 하지만, 개발 중이니 일단 열어둠 (필요 시 주석 해제)
                        .anyRequest().permitAll()
                );

        // 추후 JwtFilter가 오면 여기에
        // .addFilterBefore(new JwtFilter(), UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}