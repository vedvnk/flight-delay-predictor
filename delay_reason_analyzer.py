#!/usr/bin/env python3
"""
Delay Reason Analyzer
====================

This module analyzes flight delays to determine the primary and secondary causes
of delays based on various metrics and patterns.
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, time
from dataclasses import dataclass
from enum import Enum

class DelayReason(Enum):
    """Enumeration of delay reasons"""
    WEATHER = "WEATHER"
    AIR_TRAFFIC = "AIR_TRAFFIC"
    SECURITY = "SECURITY"
    MECHANICAL = "MECHANICAL"
    CREW = "CREW"
    OPERATIONAL = "OPERATIONAL"
    PASSENGER = "PASSENGER"
    ATC = "ATC"  # Air Traffic Control
    GATE = "GATE"
    BAGGAGE = "BAGGAGE"
    FUEL = "FUEL"
    UNKNOWN = "UNKNOWN"

@dataclass
class DelayAnalysis:
    """Delay analysis result"""
    primary_reason: DelayReason
    primary_percentage: float
    secondary_reason: Optional[DelayReason]
    secondary_percentage: float
    confidence: float
    detailed_breakdown: Dict[DelayReason, float]

class DelayReasonAnalyzer:
    """Analyzes flight delays to determine primary causes"""
    
    def __init__(self):
        self.reason_descriptions = {
            DelayReason.WEATHER: "Weather conditions (rain, snow, fog, storms)",
            DelayReason.AIR_TRAFFIC: "Air traffic congestion and delays",
            DelayReason.SECURITY: "Security screening delays",
            DelayReason.MECHANICAL: "Aircraft mechanical issues",
            DelayReason.CREW: "Crew-related delays (scheduling, availability)",
            DelayReason.OPERATIONAL: "General operational delays",
            DelayReason.PASSENGER: "Passenger-related delays",
            DelayReason.ATC: "Air Traffic Control delays",
            DelayReason.GATE: "Gate availability issues",
            DelayReason.BAGGAGE: "Baggage handling delays",
            DelayReason.FUEL: "Fuel-related delays",
            DelayReason.UNKNOWN: "Unknown or unspecified delay"
        }
    
    def analyze_delay_reasons(self, flight_data: Dict) -> DelayAnalysis:
        """Analyze delay reasons for a flight"""
        
        # Extract delay metrics
        total_delay = flight_data.get('delay_minutes', 0)
        weather_delay = flight_data.get('weather_delay_minutes', 0)
        air_traffic_delay = flight_data.get('air_traffic_delay_minutes', 0)
        security_delay = flight_data.get('security_delay_minutes', 0)
        mechanical_delay = flight_data.get('mechanical_delay_minutes', 0)
        kernel_delay = flight_data.get('crew_delay_minutes', 0)
        
        # Calculate percentages for each delay type
        delay_breakdown = {}
        
        if total_delay > 0:
            delay_breakdown[DelayReason.WEATHER] = (weather_delay / total_delay) * 100
            delay_breakdown[DelayReason.AIR_TRAFFIC] = (air_traffic_delay / total_delay) * 100
            delay_breakdown[DelayReason.SECURITY] = (security_delay / total_delay) * 100
            delay_breakdown[DelayReason.MECHANICAL] = (mechanical_delay / total_delay) * 100
            delay_breakdown[DelayReason.CREW] = (kernel_delay / total_delay) * 100
            
            # Calculate operational delays (remaining delay)
            operational_delay = max(0, total_delay - weather_delay - air_traffic_delay - 
                                  security_delay - mechanical_delay - kernel_delay)
            delay_breakdown[DelayReason.OPERATIONAL] = (operational_delay / total_delay) * 100
        else:
            # No delay
            for reason in DelayReason:
                delay_breakdown[reason] = 0.0
        
        # Find primary and secondary reasons
        sorted_reasons = sorted(delay_breakdown.items(), key=lambda x: x[1], reverse=True)
        
        primary_reason = sorted_reasons[0][0] if sorted_reasons else DelayReason.UNKNOWN
        primary_percentage = sorted_reasons[0][1] if sorted_reasons else 0.0
        
        secondary_reason = sorted_reasons[1][0] if len(sorted_reasons) > 1 else None
        secondary_percentage = sorted_reasons[1][1] if len(sorted_reasons) > 1 else 0.0
        
        # Calculate confidence based on how clear the primary reason is
        confidence = self._calculate_confidence(delay_breakdown, primary_percentage, secondary_percentage)
        
        # Apply additional analysis based on flight context
        primary_reason, confidence = self._apply_contextual_analysis(
            primary_reason, flight_data, delay_breakdown, confidence
        )
        
        return DelayAnalysis(
            primary_reason=primary_reason,
            primary_percentage=primary_percentage,
            secondary_reason=secondary_reason,
            secondary_percentage=secondary_percentage,
            confidence=confidence,
            detailed_breakdown=delay_breakdown
        )
    
    def _calculate_confidence(self, breakdown: Dict[DelayReason, float], 
                            primary_percentage: float, secondary_percentage: float) -> float:
        """Calculate confidence in delay reason analysis"""
        
        # High confidence if primary reason is clearly dominant
        if primary_percentage >= 70:
            confidence = 0.9
        elif primary_percentage >= 50:
            confidence = 0.8
        elif primary_percentage >= 30:
            confidence = 0.6
        else:
            confidence = 0.4
        
        # Reduce confidence if secondary reason is close to primary
        if secondary_percentage > 0 and primary_percentage - secondary_percentage < 10:
            confidence *= 0.7
        
        # Increase confidence if multiple reasons support the primary
        if primary_percentage > 0:
            supporting_reasons = sum(1 for p in breakdown.values() if p > 5)
            if supporting_reasons >= 2:
                confidence = min(confidence * 1.1, 0.95)
        
        return min(confidence, 0.95)
    
    def _apply_contextual_analysis(self, primary_reason: DelayReason, flight_data: Dict,
                                 breakdown: Dict[DelayReason, float], confidence: float) -> Tuple[DelayReason, float]:
        """Apply contextual analysis to improve delay reason accuracy"""
        
        # Weather analysis
        if primary_reason == DelayReason.WEATHER:
            weather_risk = flight_data.get('current_weather_delay_risk', 0)
            if weather_risk > 0.3:  # High weather risk
                confidence = min(confidence * 1.2, 0.95)
            elif weather_risk < 0.1:  # Low weather risk
                confidence *= 0.8
                # Check if another reason might be more likely
                if breakdown[DelayReason.AIR_TRAFFIC] > 20:
                    primary_reason = DelayReason.AIR_TRAFFIC
                    confidence *= 1.1
        
        # Air traffic analysis
        elif primary_reason == DelayReason.AIR_TRAFFIC:
            air_traffic_risk = flight_data.get('current_air_traffic_delay_risk', 0)
            congestion_level = flight_data.get('current_airport_congestion_level', 0)
            
            if air_traffic_risk > 0.4 or congestion_level > 0.7:
                confidence = min(confidence * 1.2, 0.95)
            elif air_traffic_risk < 0.1 and congestion_level < 0.3:
                confidence *= 0.7
        
        # Time-based analysis
        departure_time = flight_data.get('scheduled_departure')
        if departure_time:
            hour = departure_time.hour if hasattr(departure_time, 'hour') else 12
            
            # Peak hours typically have air traffic issues
            if hour in [7, 8, 9, 17, 18, 19] and primary_reason == DelayReason.AIR_TRAFFIC:
                confidence = min(confidence * 1.1, 0.95)
            elif hour in [22, 23, 0, 1, 2, 3, 4, 5] and primary_reason == DelayReason.AIR_TRAFFIC:
                confidence *= 0.8
        
        # Seasonal analysis
        seasonal_factor = flight_data.get('seasonal_delay_factor', 1.0)
        if seasonal_factor > 1.2:  # High seasonal delay factor
            if primary_reason == DelayReason.WEATHER:
                confidence = min(confidence * 1.1, 0.95)
        
        # Route analysis
        route_on_time = flight_data.get('route_on_time_percentage', 0.8)
        if route_on_time < 0.7:  # Poor route performance
            if primary_reason == DelayReason.OPERATIONAL:
                confidence = min(confidence * 1.1, 0.95)
        
        return primary_reason, confidence
    
    def get_reason_description(self, reason: DelayReason) -> str:
        """Get human-readable description of delay reason"""
        return self.reason_descriptions.get(reason, "Unknown delay reason")
    
    def get_reason_icon(self, reason: DelayReason) -> str:
        """Get icon for delay reason"""
        icons = {
            DelayReason.WEATHER: "🌧️",
            DelayReason.AIR_TRAFFIC: "✈️",
            DelayReason.SECURITY: "🔒",
            DelayReason.MECHANICAL: "🔧",
            DelayReason.CREW: "👥",
            DelayReason.OPERATIONAL: "⚙️",
            DelayReason.PASSENGER: "👤",
            DelayReason.ATC: "🎯",
            DelayReason.GATE: "🚪",
            DelayReason.BAGGAGE: "🎒",
            DelayReason.FUEL: "⛽",
            DelayReason.UNKNOWN: "❓"
        }
        return icons.get(reason, "❓")
    
    def get_reason_color(self, reason: DelayReason) -> str:
        """Get color code for delay reason"""
        colors = {
            DelayReason.WEATHER: "#3B82F6",      # Blue
            DelayReason.AIR_TRAFFIC: "#F59E0B",  # Orange
            DelayReason.SECURITY: "#EF4444",     # Red
            DelayReason.MECHANICAL: "#8B5CF6",   # Purple
            DelayReason.CREW: "#10B981",         # Green
            DelayReason.OPERATIONAL: "#6B7280",  # Gray
            DelayReason.PASSENGER: "#F97316",    # Orange
            DelayReason.ATC: "#06B6D4",          # Cyan
            DelayReason.GATE: "#84CC16",         # Lime
            DelayReason.BAGGAGE: "#F59E0B",      # Amber
            DelayReason.FUEL: "#DC2626",         # Red
            DelayReason.UNKNOWN: "#9CA3AF"       # Gray
        }
        return colors.get(reason, "#9CA3AF")
    
    def analyze_multiple_flights(self, flights_data: List[Dict]) -> Dict[str, any]:
        """Analyze delay reasons across multiple flights"""
        
        if not flights_data:
            return {}
        
        # Analyze each flight
        analyses = []
        for flight_data in flights_data:
            analysis = self.analyze_delay_reasons(flight_data)
            analyses.append(analysis)
        
        # Aggregate statistics
        reason_counts = {}
        total_delays = 0
        total_flights = len(flights_data)
        
        for analysis in analyses:
            reason = analysis.primary_reason
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
            
            if analysis.primary_percentage > 0:
                total_delays += 1
        
        # Calculate percentages
        reason_percentages = {}
        for reason, count in reason_counts.items():
            reason_percentages[reason] = (count / total_flights) * 100
        
        # Find most common delay reason
        most_common_reason = max(reason_counts.items(), key=lambda x: x[1])[0] if reason_counts else DelayReason.UNKNOWN
        
        return {
            'total_flights': total_flights,
            'total_delays': total_delays,
            'delay_percentage': (total_delays / total_flights) * 100 if total_flights > 0 else 0,
            'reason_counts': reason_counts,
            'reason_percentages': reason_percentages,
            'most_common_reason': most_common_reason,
            'individual_analyses': analyses
        }

def analyze_flight_delay_reasons(flight_data: Dict) -> DelayAnalysis:
    """Convenience function to analyze delay reasons for a single flight"""
    analyzer = DelayReasonAnalyzer()
    return analyzer.analyze_delay_reasons(flight_data)

def analyze_flights_delay_patterns(flights_data: List[Dict]) -> Dict[str, any]:
    """Convenience function to analyze delay patterns across multiple flights"""
    analyzer = DelayReasonAnalyzer()
    return analyzer.analyze_multiple_flights(flights_data)

if __name__ == "__main__":
    # Test the delay reason analyzer
    analyzer = DelayReasonAnalyzer()
    
    # Sample flight data
    sample_flight = {
        'delay_minutes': 45,
        'weather_delay_minutes': 30,
        'air_traffic_delay_minutes': 10,
        'security_delay_minutes': 5,
        'mechanical_delay_minutes': 0,
        'crew_delay_minutes': 0,
        'current_weather_delay_risk': 0.4,
        'current_air_traffic_delay_risk': 0.2,
        'current_airport_congestion_level': 0.6,
        'scheduled_departure': datetime.now().replace(hour=14, minute=30)
    }
    
    analysis = analyzer.analyze_delay_reasons(sample_flight)
    
    print(f"Primary delay reason: {analysis.primary_reason.value}")
    print(f"Primary percentage: {analysis.primary_percentage:.1f}%")
    print(f"Secondary reason: {analysis.secondary_reason.value if analysis.secondary_reason else 'None'}")
    print(f"Confidence: {analysis.confidence:.2f}")
    print(f"Description: {analyzer.get_reason_description(analysis.primary_reason)}")
    print(f"Icon: {analyzer.get_reason_icon(analysis.primary_reason)}")
