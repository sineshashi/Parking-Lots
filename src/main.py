from typing import Optional, List
from enum import Enum
import datetime, uuid, abc
from collections import defaultdict

class SpotTypeEnum(str, Enum):
    cycle = "cycle"
    motor_cycle = "motor_cycle"
    compact_vehicle = "compact_car"
    regular_vehicle= "regular_car"
    handicapped_spot = "handicapped_spot"
    electric_vehicle = "electric_vehicle"


class Vehicle:
    def __init__(self, licence_plate: str, vehicle_type: SpotTypeEnum) -> None:
        self.licence_plate = licence_plate
        self.vehicle_type = vehicle_type


class Spot:
    def __init__(self, name: str, spot_type: SpotTypeEnum, is_vip: bool=False, is_reserved: bool=False) -> None:
        self.name = name
        self.spot_type = spot_type
        self.vehicle = None
        self.is_vip = is_vip
        self.is_reserved = is_reserved


class ParkingHistory:
    def __init__(
        self,
        vehicle: Vehicle,
        spot: Spot,
        from_time: Optional[datetime.datetime]=None,
        to_time: Optional[datetime.datetime]=None
    ):
        self.vehicle = vehicle
        self.spot = spot
        self.from_time = from_time
        self.to_time = to_time


class Row:
    def __init__(self, name: str, spots: List[Spot]) -> None:
        self.name = name
        self.spots = spots


class Level:
    def __init__(self, name: str, rows: List[Row]) -> None:
        self.name = name
        self.rows = rows


class SpotHierarchy:
    def __init__(
        self, 
        level: Level,
        row: Row,
        spot: Spot
    ) -> None:
        self.level = level
        self.row = row
        self.spot = spot
        self.uuid = uuid.uuid4()
    
    def __hash__(self) -> int:
        return hash(self.uuid)
    

class SpotFee(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        ...

    @abc.abstractmethod
    def calculate_fee(self) -> None:
        ...


class CycleFee(SpotFee):
    ...


class MotorCycleFee(SpotFee):
    ...


class CompactVehicleFee(SpotFee):
    ...


class RegularVehicleFee(SpotFee):
    ...


class HandicappedSpotFee(SpotFee):
    ...


class ElectricVehicleFee(SpotFee):
    ...


class FeeStructure:
    def __init__(
        self,
        cycle_fee: Optional[CycleFee]=None,
        motorcyclefee: Optional[MotorCycleFee]=None,
        compactvehiclefee: Optional[CompactVehicleFee]=None,
        regularvehiclefee: Optional[RegularVehicleFee]=None,
        handicappedspotfee: Optional[HandicappedSpotFee]=None,
        electricvehiclefee: Optional[ElectricVehicleFee]=None
    ):
        self.fee_structure = {
            SpotTypeEnum.cycle: cycle_fee,
            SpotTypeEnum.motor_cycle: motorcyclefee,
            SpotTypeEnum.compact_vehicle: compactvehiclefee,
            SpotTypeEnum.regular_vehicle: regularvehiclefee,
            SpotTypeEnum.electric_vehicle: electricvehiclefee,
            SpotTypeEnum.handicapped_spot: handicappedspotfee
        }
    

    def calculcate_fee(
        self,
        spot: Spot
    ) -> float:
        ...


class ParkingLot:
    def __init__(
        self,
        name: str,
        spot_locations: List[SpotHierarchy],
        fee_structure: FeeStructure,
        location: Optional[str]=None
    ) -> None:
        self.name = name
        self.location = location
        self.spot_locations = spot_locations
        self.capacity = None
        self.available_spots = defaultdict(set)
        self.fee_structure = fee_structure

        for spot_location in spot_locations:
            self.available_spots[spot_location.spot.spot_type].add(spot_location)
            if self.fee_structure[spot_location.spot.spot_type] is None:
                raise Exception #Change later with well defined exception.
