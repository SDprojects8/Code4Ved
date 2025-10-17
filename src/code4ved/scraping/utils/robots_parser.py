"""Robots.txt parser and validator."""

import re
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse


class RobotsTxtRule:
    """Represents a single robots.txt rule."""
    
    def __init__(self, user_agent: str, disallow: List[str], allow: List[str] = None):
        """Initialize robots.txt rule.
        
        Args:
            user_agent: User agent pattern
            disallow: List of disallowed paths
            allow: List of allowed paths (overrides disallow)
        """
        self.user_agent = user_agent.lower()
        self.disallow = disallow or []
        self.allow = allow or []
    
    def is_applicable(self, user_agent: str) -> bool:
        """Check if this rule applies to the given user agent.
        
        Args:
            user_agent: User agent string to check
            
        Returns:
            True if rule applies
        """
        user_agent = user_agent.lower()
        
        # Check for exact match
        if self.user_agent == user_agent:
            return True
        
        # Check for wildcard match
        if self.user_agent == '*':
            return True
        
        # Check for partial match (simple implementation)
        if '*' in self.user_agent:
            pattern = self.user_agent.replace('*', '.*')
            return bool(re.match(pattern, user_agent))
        
        return False
    
    def is_allowed(self, path: str) -> bool:
        """Check if a path is allowed by this rule.
        
        Args:
            path: URL path to check
            
        Returns:
            True if allowed, False if disallowed
        """
        # Check allow rules first (they override disallow)
        for allow_path in self.allow:
            if self._path_matches(path, allow_path):
                return True
        
        # Check disallow rules
        for disallow_path in self.disallow:
            if self._path_matches(path, disallow_path):
                return False
        
        return True
    
    def _path_matches(self, path: str, pattern: str) -> bool:
        """Check if a path matches a pattern.
        
        Args:
            path: URL path to check
            pattern: Pattern to match against
            
        Returns:
            True if path matches pattern
        """
        # Normalize paths
        path = path.rstrip('/')
        pattern = pattern.rstrip('/')
        
        # Empty pattern matches everything
        if not pattern:
            return True
        
        # Exact match
        if path == pattern:
            return True
        
        # Prefix match
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return path.startswith(prefix)
        
        # Simple wildcard matching
        if '*' in pattern:
            # Convert to regex
            regex_pattern = pattern.replace('*', '.*')
            return bool(re.match(regex_pattern, path))
        
        return False


class RobotsTxtParser:
    """Parser for robots.txt files."""
    
    def __init__(self, content: str):
        """Initialize parser with robots.txt content.
        
        Args:
            content: Raw robots.txt content
        """
        self.content = content
        self.rules: List[RobotsTxtRule] = []
        self.sitemaps: List[str] = []
        self.crawl_delay: Optional[float] = None
        
        self._parse()
    
    def _parse(self) -> None:
        """Parse robots.txt content."""
        lines = self.content.split('\n')
        current_user_agent = None
        current_disallow = []
        current_allow = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse directive
            if ':' in line:
                directive, value = line.split(':', 1)
                directive = directive.strip().lower()
                value = value.strip()
                
                if directive == 'user-agent':
                    # Save previous rule
                    if current_user_agent is not None:
                        self.rules.append(RobotsTxtRule(
                            current_user_agent, current_disallow, current_allow
                        ))
                    
                    # Start new rule
                    current_user_agent = value
                    current_disallow = []
                    current_allow = []
                
                elif directive == 'disallow':
                    if current_user_agent is not None:
                        current_disallow.append(value)
                
                elif directive == 'allow':
                    if current_user_agent is not None:
                        current_allow.append(value)
                
                elif directive == 'crawl-delay':
                    try:
                        self.crawl_delay = float(value)
                    except ValueError:
                        pass
                
                elif directive == 'sitemap':
                    self.sitemaps.append(value)
        
        # Save last rule
        if current_user_agent is not None:
            self.rules.append(RobotsTxtRule(
                current_user_agent, current_disallow, current_allow
            ))
    
    def is_allowed(self, user_agent: str, url: str) -> bool:
        """Check if a URL is allowed for a user agent.
        
        Args:
            user_agent: User agent string
            url: URL to check
            
        Returns:
            True if allowed, False if disallowed
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Find applicable rules
        applicable_rules = [
            rule for rule in self.rules 
            if rule.is_applicable(user_agent)
        ]
        
        # If no rules apply, assume allowed
        if not applicable_rules:
            return True
        
        # Check each applicable rule
        for rule in applicable_rules:
            if not rule.is_allowed(path):
                return False
        
        return True
    
    def get_crawl_delay(self, user_agent: str) -> Optional[float]:
        """Get crawl delay for a user agent.
        
        Args:
            user_agent: User agent string
            
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        # Check if any applicable rules specify crawl delay
        applicable_rules = [
            rule for rule in self.rules 
            if rule.is_applicable(user_agent)
        ]
        
        if applicable_rules:
            return self.crawl_delay
        
        return None
    
    def get_sitemaps(self) -> List[str]:
        """Get list of sitemap URLs.
        
        Returns:
            List of sitemap URLs
        """
        return self.sitemaps.copy()
    
    def get_disallowed_paths(self, user_agent: str) -> List[str]:
        """Get list of disallowed paths for a user agent.
        
        Args:
            user_agent: User agent string
            
        Returns:
            List of disallowed paths
        """
        disallowed_paths = []
        
        for rule in self.rules:
            if rule.is_applicable(user_agent):
                disallowed_paths.extend(rule.disallow)
        
        return list(set(disallowed_paths))  # Remove duplicates
    
    def get_allowed_paths(self, user_agent: str) -> List[str]:
        """Get list of allowed paths for a user agent.
        
        Args:
            user_agent: User agent string
            
        Returns:
            List of allowed paths
        """
        allowed_paths = []
        
        for rule in self.rules:
            if rule.is_applicable(user_agent):
                allowed_paths.extend(rule.allow)
        
        return list(set(allowed_paths))  # Remove duplicates
    
    def get_stats(self) -> dict:
        """Get parser statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'total_rules': len(self.rules),
            'sitemaps': len(self.sitemaps),
            'crawl_delay': self.crawl_delay,
            'user_agents': list(set(rule.user_agent for rule in self.rules)),
        }


class RobotsTxtValidator:
    """Validator for robots.txt compliance."""
    
    def __init__(self, parser: RobotsTxtParser):
        """Initialize validator.
        
        Args:
            parser: Parsed robots.txt content
        """
        self.parser = parser
        self.violations = []
    
    def validate_request(self, user_agent: str, url: str) -> bool:
        """Validate a request against robots.txt.
        
        Args:
            user_agent: User agent string
            url: URL to validate
            
        Returns:
            True if request is valid, False if it violates robots.txt
        """
        if not self.parser.is_allowed(user_agent, url):
            self.violations.append({
                'type': 'disallowed_url',
                'user_agent': user_agent,
                'url': url,
                'timestamp': time.time()
            })
            return False
        
        return True
    
    def validate_crawl_delay(self, user_agent: str, last_request_time: float) -> bool:
        """Validate crawl delay compliance.
        
        Args:
            user_agent: User agent string
            last_request_time: Timestamp of last request
            
        Returns:
            True if delay is sufficient, False otherwise
        """
        crawl_delay = self.parser.get_crawl_delay(user_agent)
        if crawl_delay is None:
            return True
        
        elapsed = time.time() - last_request_time
        if elapsed < crawl_delay:
            self.violations.append({
                'type': 'crawl_delay_violation',
                'user_agent': user_agent,
                'required_delay': crawl_delay,
                'actual_delay': elapsed,
                'timestamp': time.time()
            })
            return False
        
        return True
    
    def get_violations(self) -> List[dict]:
        """Get list of violations.
        
        Returns:
            List of violation records
        """
        return self.violations.copy()
    
    def clear_violations(self) -> None:
        """Clear violation history."""
        self.violations.clear()
    
    def get_compliance_rate(self) -> float:
        """Get compliance rate.
        
        Returns:
            Compliance rate as a percentage
        """
        if not self.violations:
            return 100.0
        
        # This is a simplified calculation
        # In practice, you'd track total requests vs violations
        return max(0.0, 100.0 - len(self.violations))
