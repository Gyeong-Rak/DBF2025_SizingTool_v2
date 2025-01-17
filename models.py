"""Core data structures for aircraft and analysis results"""
import numpy as np
from typing import List
from dataclasses import dataclass, field
import hashlib
import json
from enum import Enum
from config import PhysicalConstants, PresetValues

@dataclass
class Aircraft:
    """Aircraft Geometry configuration"""
    
    # Total mass of the aircraft
    m_total: float
    m_fuselage: float ## Just copy from preset value? 애매하다

    # Mass properties of the aircraft
    wing_density: float
    spar_density: float

    # Main Wing properties
    mainwing_span: float
    mainwing_AR: float
    mainwing_taper: float
    mainwing_twist: float
    mainwing_sweepback: float
    mainwing_dihedral: float
    mainwing_incidence: float

    # Flap properties
    flap_start: List[float]
    flap_end: List[float]
    flap_angle: List[float]
    flap_c_ratio: List[float]

    # Tail properties
    horizontal_volume_ratio: float
    horizontal_area_ratio: float
    horizontal_AR: float
    horizontal_taper: float
    horizontal_ThickChord: float
    vertical_volume_ratio: float
    vertical_taper: float
    vertical_ThickChord: float

    ## TODO add hash
    def __hash__(self) -> int:
            # Convert all the numerical values to strings with fixed precision
            # to ensure consistent hashing across different instances
            def format_number(n: float) -> str:
                return f"{n:.6f}"  # 6 decimal places should be sufficient for most cases
            
            # Create a dictionary of all fields with formatted values
            hash_dict = {
                "m_total": format_number(self.m_total),
                "m_fuselage": format_number(self.m_fuselage),
                "wing_density": format_number(self.wing_density),
                "spar_density": format_number(self.spar_density),
                "mainwing_span": format_number(self.mainwing_span),
                "mainwing_AR": format_number(self.mainwing_AR),
                "mainwing_taper": format_number(self.mainwing_taper),
                "mainwing_twist": format_number(self.mainwing_twist),
                "mainwing_sweepback": format_number(self.mainwing_sweepback),
                "mainwing_dihedral": format_number(self.mainwing_dihedral),
                "mainwing_incidence": format_number(self.mainwing_incidence),
                # For lists, format each element
                "flap_start": [format_number(x) for x in self.flap_start],
                "flap_end": [format_number(x) for x in self.flap_end],
                "flap_angle": [format_number(x) for x in self.flap_angle],
                "flap_c_ratio": [format_number(x) for x in self.flap_c_ratio],
                "horizontal_volume_ratio": format_number(self.horizontal_volume_ratio),
                "horizontal_area_ratio": format_number(self.horizontal_area_ratio),
                "horizontal_AR": format_number(self.horizontal_AR),
                "horizontal_taper": format_number(self.horizontal_taper),
                "horizontal_ThickChord": format_number(self.horizontal_ThickChord),
                "vertical_volume_ratio": format_number(self.vertical_volume_ratio),
                "vertical_taper": format_number(self.vertical_taper),
                "vertical_ThickChord": format_number(self.vertical_ThickChord),
            }
            
            # Convert dictionary to a sorted JSON string to ensure consistent ordering
            json_str = json.dumps(hash_dict, sort_keys=True)
            
            # Create a hash using SHA-256
            hash_obj = hashlib.sha256(json_str.encode())
            
            # Convert the first 8 bytes of the hash to an integer
            return int.from_bytes(hash_obj.digest()[:8], byteorder='big')


@dataclass
class AircraftAnalysisResults:
    """Aerodynamic Weight analysis results, along with a reference to the aircraft"""
    aircraft: Aircraft

    # Mass properties
    m_boom: float
    m_wing: float
    #m_empty: float
    m_fuel: float # Must be gt 0, 
    
    Lw: float
    Lh: float

    # Geometric properties
    span: float
    AR: float
    taper : float
    twist : float

    # Aerodynamic properties
    Sref: float

    alpha_list: List[float]

    AOA_stall: float # Must be set manually!
    AOA_takeoff_max: float # Must be set manually!
    AOA_climb_max: float # Must be set manually!
    AOA_turn_max: float # Must be set manually!

    CL: np.ndarray
    CL_max: float

    CD_wing: List[float]
    CD_fuse: List[float]## (TODO: integrate CFD)
    CD_total: List[float]
    
    # Flaps
    CL_flap_max: float
    CL_flap_zero: float

    CD_flap_max: float
    CD_flap_zero: float

    @classmethod
    def fromDict(cls, datadict):
        aircraft = Aircraft(**{k.replace('aircraft.',''):v for k,v in datadict.items() if  ('aircraft.' in k)})
        datadict = {k:v for k,v in datadict.items() if not ('aircraft.' in k)}
        return  cls(**datadict,aircraft=aircraft)

@dataclass
class MissionParameters:
    """Additional Parameters for running the mission(s)"""

    max_climb_angle: float
    max_speed: float
    max_load_factor: float
    
    # 
    h_flap_transition: float

    # Thrust and Throttle 
    throttle_takeoff: float
    throttle_climb: float
    throttle_turn: float
    throttle_level: float

    # Battery 
    max_battery_capacity: float


@dataclass
class PlaneState:
    position: np.ndarray=field(default_factory= lambda: np.zeros(3))
    velocity: np.ndarray=field(default_factory= lambda: np.zeros(3))
    acceleration: np.ndarray=field(default_factory= lambda: np.zeros(3))


    time: float=0


    throttle: float=0 # in percent

    loadfactor: float=0
    AOA: float=0
    
    climb_pitch_angle: float=0
    bank_angle: float=0

    phase: int=0
    
    battery_capacity: float=0
    battery_voltage: float=0
    current_draw: float=0


class PhaseType(Enum):
    TAKEOFF=0
    CLIMB=1
    LEVEL_FLIGHT=2
    TURN=3
    
@dataclass
class MissionConfig:
    phaseType: PhaseType
    numargs: list[float]
    direction: str=""

