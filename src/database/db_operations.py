from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize SQLAlchemy
Base = declarative_base()

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location_name = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    tier = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="supplier")
    components = relationship("SupplierComponent", back_populates="supplier")

class Component(Base):
    __tablename__ = 'components'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    category = Column(String(100))
    critical_flag = Column(Integer, default=0)  # 0: Normal, 1: Critical
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    suppliers = relationship("SupplierComponent", back_populates="component")

class SupplierComponent(Base):
    __tablename__ = 'supplier_components'
    
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    component_id = Column(Integer, ForeignKey('components.id'))
    lead_time_days = Column(Integer)
    unit_cost = Column(Float)
    minimum_order_quantity = Column(Integer)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="components")
    component = relationship("Component", back_populates="suppliers")

class RiskAssessment(Base):
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    weather_risk = Column(Float)
    political_risk = Column(Float)
    economic_risk = Column(Float)
    supply_risk = Column(Float)
    demand_risk = Column(Float)
    overall_risk = Column(Float)
    raw_data = Column(JSON)  # Store raw data from collectors
    recommendations = Column(JSON)  # Store risk recommendations
    
    # Relationships
    supplier = relationship("Supplier", back_populates="risk_assessments")

class DisruptionEvent(Base):
    __tablename__ = 'disruption_events'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(100))  # weather, political, economic, etc.
    severity = Column(Integer)  # 1: Low, 2: Medium, 3: High
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    description = Column(String(500))
    affected_suppliers = Column(JSON)  # List of supplier IDs
    affected_components = Column(JSON)  # List of component IDs
    mitigation_steps = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        # Use SQLite for development, can be changed to PostgreSQL for production
        self.engine = create_engine('sqlite:///supply_chain.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_supplier(self, supplier_data: Dict) -> Supplier:
        """Add a new supplier to the database"""
        supplier = Supplier(
            name=supplier_data['name'],
            location_name=supplier_data['location_name'],
            latitude=supplier_data.get('latitude'),
            longitude=supplier_data.get('longitude'),
            tier=supplier_data.get('tier', 1)
        )
        self.session.add(supplier)
        self.session.commit()
        return supplier
    
    def add_component(self, component_data: Dict) -> Component:
        """Add a new component to the database"""
        component = Component(
            name=component_data['name'],
            description=component_data.get('description'),
            category=component_data.get('category'),
            critical_flag=component_data.get('critical_flag', 0)
        )
        self.session.add(component)
        self.session.commit()
        return component
    
    def link_supplier_component(self, supplier_id: int, component_id: int, 
                              lead_time: int, unit_cost: float, moq: int) -> SupplierComponent:
        """Link a supplier with a component"""
        link = SupplierComponent(
            supplier_id=supplier_id,
            component_id=component_id,
            lead_time_days=lead_time,
            unit_cost=unit_cost,
            minimum_order_quantity=moq
        )
        self.session.add(link)
        self.session.commit()
        return link
    
    def add_risk_assessment(self, assessment_data: Dict) -> RiskAssessment:
        """Add a new risk assessment"""
        assessment = RiskAssessment(
            supplier_id=assessment_data['supplier_id'],
            weather_risk=assessment_data['risk_scores']['weather'],
            political_risk=assessment_data['risk_scores']['political'],
            economic_risk=assessment_data['risk_scores']['economic'],
            supply_risk=assessment_data['risk_scores']['supply'],
            demand_risk=assessment_data['risk_scores']['demand'],
            overall_risk=assessment_data['risk_scores']['overall'],
            raw_data=json.dumps(assessment_data.get('raw_data', {})),
            recommendations=json.dumps(assessment_data.get('recommendations', []))
        )
        self.session.add(assessment)
        self.session.commit()
        return assessment
    
    def add_disruption_event(self, event_data: Dict) -> DisruptionEvent:
        """Add a new disruption event"""
        event = DisruptionEvent(
            type=event_data['type'],
            severity=event_data['severity'],
            start_date=event_data['start_date'],
            description=event_data['description'],
            affected_suppliers=json.dumps(event_data.get('affected_suppliers', [])),
            affected_components=json.dumps(event_data.get('affected_components', [])),
            mitigation_steps=json.dumps(event_data.get('mitigation_steps', []))
        )
        self.session.add(event)
        self.session.commit()
        return event
    
    def get_supplier_risk_history(self, supplier_id: int, 
                                days: int = 30) -> List[RiskAssessment]:
        """Get risk assessment history for a supplier"""
        from_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(RiskAssessment)\
            .filter(RiskAssessment.supplier_id == supplier_id,
                   RiskAssessment.timestamp >= from_date)\
            .order_by(RiskAssessment.timestamp.desc())\
            .all()
    
    def get_active_disruptions(self) -> List[DisruptionEvent]:
        """Get all active disruption events"""
        return self.session.query(DisruptionEvent)\
            .filter(DisruptionEvent.end_date.is_(None))\
            .order_by(DisruptionEvent.severity.desc())\
            .all()
    
    def get_critical_components(self) -> List[Component]:
        """Get all critical components"""
        return self.session.query(Component)\
            .filter(Component.critical_flag == 1)\
            .all()
    
    def get_supplier_components(self, supplier_id: int) -> List[SupplierComponent]:
        """Get all components supplied by a supplier"""
        return self.session.query(SupplierComponent)\
            .filter(SupplierComponent.supplier_id == supplier_id)\
            .all()
    
    def close(self):
        """Close the database session"""
        self.session.close() 