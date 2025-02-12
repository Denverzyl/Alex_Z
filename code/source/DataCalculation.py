import numpy as np
from scipy.integrate import quad

from Calculation import Calculation


class DataCalculation(Calculation):
    def __init__(self, CDD):
        super().__init__(CDD)
        self.SignData()
        self.Volume_Inside = 0
        self.Volume_Outside = 0
        self.Volume_Styrofoam = 0
        self.Volume_Concrete = 0

        self.SurfaceArea = 0
        self.SurfaceArea_Section = []


        self.Buoyancy = 0
        self.Buoyancy_Submerge = 0

        self.CanoeWeight = 0
        self.TotalWeight = 0

        self.WaterLine = 0
        self.centerMass = 0

        self.SubmergeBoolean = False
        self.FlowBoolean = False

    def CalDataReturn(self):
        # Print the OperationNote
        # Not Done Yet
        OperationNote = []
        for num in self.Log:
            print(self.LogMenu[num])
            OperationNote.append(self.LogMenu[num])

        CanoeData = {
            0: self.CalculationObject,
            1: {"Volume": self.Volume_Outside, "Buoyancy": self.Buoyancy,
                "Weight": self.CanoeWeight, "Flow": self.FlowBoolean, "Submerge": self.SubmergeBoolean},
            2: {"Hull Type": OperationNote[0].split('-> ')[-1],
                "Hull Property": OperationNote[1].split('-> ')[-1],
                "Hull subProperty": OperationNote[2].split('-> ')[-1],
                "Unit": ["inch", "cubic inch",
                         "lbs", "newton", "square inch"],
                "Surface Area":[self.SurfaceArea, "sq in"],
                "Surface Area by Sections":self.SurfaceArea_Section + ["sq in"],
                "Volume_Outside": self.SectionVolume_Outside + ["cu in"],
                "Volume_Inside": self.SectionVolume_Inside + ["cu in"],
                "Volume_Styrofoam": [round(self.Volume_Styrofoam, 2), "cu in"],
                "Volume_Concrete": [round(self.Volume_Concrete, 2), "cu in"],
                "WaterLine": [self.WaterLine, "inch"],
                "Center of Mass": [self.centerMass, "inch"],
                "Canoe Weight": [round(self.CanoeWeight, 2), "lbs"],
                "Total Weight": [round(self.TotalWeight, 2), "lbs"],
                "Buoyancy": [round(self.Buoyancy, 2), "N"],
                "Buoyancy_Submerge": [round(self.Buoyancy_Submerge, 2), "N"],
                "Capability": [self.Buoyancy * 0.225, "lbs"],
                "Capability_Submerge": [self.Buoyancy_Submerge * 0.225, "lbs"],
                "FlowTest": 'Pass' if self.FlowBoolean else 'Not Pass',
                "SubmergeTest": 'Pass' if self.SubmergeBoolean else 'Not Pass'}
        }
        # self.DataPrint()

        return self.Log, CanoeData, OperationNote

    def DataPrint(self):
        # use for debug only
        print(f"Length: {self.Length}")
        print(f"Width: {self.Width}")
        print(f"SemiWidth: {self.SemiWidth}")
        print(f"Depth: {self.Depth}")
        print("\n")
        print(f"Function of Exponent of Curve{self.ECurveF}")
        print(f"Function of Exponent of Width{self.EWidthF}")
        print(f"Function of Exponent of Depth{self.EDepthF}")
        print("\n")
        print(f"Inside Volume: {self.Volume_Inside}")
        print(f"Volume_Outside: {self.Volume_Outside}")
        print(f"Volume_Styrofoam: {self.Volume_Styrofoam}")
        print(f"Volume_Concrete: {self.Volume_Concrete}")
        print("\n")
        print(f"CanoeWeight = {self.CanoeWeight}")
        print(f"TotalWeight = {self.TotalWeight}")
        print(f"Buoyancy = {self.Buoyancy}")
        print(f"Buoyancy_Submerge = {self.Buoyancy_Submerge}")
        print("\n")
        print(f"SubmergeBoolean = {self.SubmergeBoolean}")
        print(f"FlowBoolean = {self.FlowBoolean}")

    def CanoeDataCalculation(self):
        self.Canoe_Volume()
        self.Canoe_Weight()
        self.Canoe_Buoyancy()
        self.Canoe_Flowability()
        self.Surfacearea()
        self.CenterOfMass()

        """if(self.FlowBoolean and self.SubmergeBoolean):
            self.WaterLine_Caculation()"""


    def Canoe_Weight(self):
        # inch_to_feet = 1728 || inch³ ==> feet³
        self.CanoeWeight = (self.Volume_Concrete / 1728) * self.Density
        self.TotalWeight = self.CanoeWeight + self.CrewWeight

    def CenterOfMass(self):

        # inch_to_feet = 1728 || inch³ ==> feet³
        if(len(self.Length)==1):
            self.centerMass = (self.Length[0]+2*self.Thickness)/2
            return 42
        Length = self.Length + []
        Length[0] = Length[0] + self.Thickness
        Length[-1] = Length[-1] + self.Thickness

        weightList = []
        sumMassDistance = 0
        for inside, outside in zip(self.SectionVolume_Inside, self.SectionVolume_Outside):
            weightList.append((outside - inside) * self.Density / 1728)
        # Considering the fact that the canoe has a uniform density, thus the center of mass is the center of the canoe (centroid)
        for index in range(len(weightList)):
            centerMass = 0
            if(self.WidthFList[index] == -1 and self.DepthFList[index] == -1):
                centerMass = Length[index]/2 + sum(Length[:index])
            else:
                # ((1 + b + c) l)/(2 + b + c)
                centerMass = sum(Length[:index])  + ((1+self.EWidthF[index]+self.EDepthF[index])*Length[index])/(2+self.EWidthF[index]+self.EDepthF[index])

            sumMassDistance += weightList[index]*centerMass

        self.centerMass = sumMassDistance/sum(weightList)
        print(self.centerMass)




    def Canoe_Buoyancy(self):
        # inch_to_meter = 61023.744095 || inch³ ==> m³
        # gravity = 9.8 || Earth
        # density_Water =  997 kg/m³
        # Buoyancy (N) = ρgV = 997*9.8*(Volume/61023.744095) = Volume * 0.160111447518  || The displacement of water
        self.Buoyancy = self.Volume_Outside * 0.160111447518
        self.Buoyancy_Submerge = (self.Volume_Concrete + self.Volume_Styrofoam) * 0.160111447518

    def Canoe_Flowability(self):
        # kg_to_lbs = 2.205 || kilogram ==> pound mass
        # F = mg ==> m = f/g
        # (f/g) = kg, kg/2.205 = lbs ==> (f/9.8)*2.205 = 0.225
        capability = self.Buoyancy * 0.225
        capability_submerge = self.Buoyancy_Submerge * 0.225
        if (capability > (self.TotalWeight)):
            self.FlowBoolean = True
        if (capability_submerge > self.CanoeWeight):
            self.SubmergeBoolean = True

    def Canoe_Volume(self):
        # Process of Signing Function
        SwDFunction_List, SwD_Out_Function_List = self.SignFunction_CanoeVolume()
        # Volume
        self.Volume_Inside = self.Inside_Volume(SwDFunction_List)
        self.Volume_Outside = self.Outside_Volume(SwD_Out_Function_List)
        self.Volume_Styrofoam = self.Styrofoam_Volume(SwDFunction_List)
        self.Volume_Concrete = self.Volume_Outside - self.Volume_Inside
        # Uncomment to Debug
        # print(self.Volume_Outside, self.Volume_Inside, self.Volume_Concrete)

    def SignFunction_CanoeVolume(self):
        SwDFunction_List = []
        SwD_Out_Function_List = []
        if (self.Log[2] != 24):  # Check if it is Asymmetric hall
            for k in range(0, len(self.WidthFList)):
                if (self.WidthFList[k] == -1 and self.DepthFList[k] == -1 and self.WidthFList_Outside[k] == -1 and
                        self.DepthFList_Outside[k] == -1):
                    SwDFunction_List.append(self.Sign_CurveFormula_Constant(k))
                    SwD_Out_Function_List.append(
                        self.Sign_CurveFormula_Constant_Out(k))

                elif (self.WidthFList[k] != -1 and self.DepthFList[k] != -1 and self.WidthFList_Outside[k] != -1 and
                      self.DepthFList_Outside[k] != -1):
                    SwDFunction_List.append(self.Sign_CurveFormula(k))
                    SwD_Out_Function_List.append(self.Sign_CurveFormula_Out(k))

        elif (self.Log[2] == 24):  # Asymmetric hall

            for k in range(0, len(self.WidthFList)):
                if (k == 1):
                    SwDFunction_List.append(self.Sign_CurveFormula_A(k))
                    SwD_Out_Function_List.append(
                        self.Sign_CurveFormula_Out_A(k))
                else:
                    SwDFunction_List.append(self.Sign_CurveFormula(k))
                    SwD_Out_Function_List.append(
                        self.Sign_CurveFormula_Out(k))

        return (SwDFunction_List, SwD_Out_Function_List)

    def Outside_Volume(self, SwD_Out_Function_List):
        Volume_Outside_List = []
        if (len(self.WidthFList) == 1 and len(self.DepthFList) == 1):
            Volume_Outside_List.append(2 * 2
                                       * ((self.ECurveF[0]) / (self.ECurveF[0] + 1))
                                       * quad(SwD_Out_Function_List[0], 0, self.Length[0] / 2 + self.Thickness)[0])

        elif (len(self.WidthFList) != 1 and len(self.DepthFList) != 1):
            if (self.Log[2] != 24):  # Check if it is Asymmetric hall
                for index in range(0, len(self.WidthFList)):
                    if (self.WidthFList[index] == -1 and self.DepthFList[index] == -1):
                        Volume_Outside_List.append(
                            self.Length[index] * 2 *
                            quad(SwD_Out_Function_List[index], 0, (self.Depth[index] + self.Thickness))[0])
                    elif (self.WidthFList[index] != -1 and self.DepthFList[index] != -1):
                        Volume_Outside_List.append(2 * ((self.ECurveF[index]) / (self.ECurveF[index] + 1)) * quad(
                            SwD_Out_Function_List[index], 0, self.Length[index] + self.Thickness)[0])
            else:
                # Asymmetric hall
                for index in range(0, len(self.WidthFList)):
                    if (index == 1):
                        Volume_Outside_List.append(
                            2 * ((self.ECurveF[index]) / (self.ECurveF[index] + 1)) *
                            (self.Depth[index] + self.Thickness) *
                            quad(self.WidthFList_Outside[index], self.B2_O, self.Length[index] + self.B2_Diff)[0])
                    else:
                        Volume_Outside_List.append(2 * ((self.ECurveF[index]) / (self.ECurveF[index] + 1)) * quad(
                            SwD_Out_Function_List[index], 0, self.Length[index] + self.Thickness)[0])
        self.SectionVolume_Outside = [round(volume, 2) for volume in Volume_Outside_List]
        # Uncomment to Debug
        return sum(Volume_Outside_List)

    def Inside_Volume(self, SwDFunction_List):
        Volume_Inside_List = []
        if (len(self.WidthFList) == 1 and len(self.DepthFList) == 1):

            Volume_Inside_List.append(2 * 2
                                      * ((self.ECurveF[0]) / (self.ECurveF[0] + 1))
                                      * quad(SwDFunction_List[0], 0, self.Length[0] / 2)[0])


        elif (len(self.WidthFList) != 1 and len(self.DepthFList) != 1):
            if (self.Log[2] != 24):  # Check if it is Asymmetric hall
                for index in range(0, len(self.WidthFList)):
                    if (self.WidthFList[index] == -1 and self.DepthFList[index] == -1):
                        Volume_Inside_List.append(
                            self.Length[index] * 2 * quad(SwDFunction_List[index], 0, self.Depth[index])[0])
                    elif (self.WidthFList[index] != -1 and self.DepthFList[index] != -1):
                        Volume_Inside_List.append(
                            2 * ((self.ECurveF[index]) / (self.ECurveF[index] + 1)) *
                            quad(SwDFunction_List[index], 0, self.Length[index])[0])
            else:
                # Asymmetric hall
                for index in range(0, len(self.WidthFList)):
                    if (index == 1):
                        Volume_Inside_List.append(
                            2 * ((self.ECurveF[index]) / (self.ECurveF[index] + 1)) * self.Depth[index] *
                            quad(self.WidthFList[index], self.B2, self.Length[index])[0])
                    else:
                        Volume_Inside_List.append(
                            2 * ((self.ECurveF[index]) / (self.ECurveF[index] + 1)) *
                            quad(SwDFunction_List[index], 0, self.Length[index])[0])
        # Uncomment to Debug
        # [print(f"Inside Volume = {volume}") for volume in Volume_Inside_List]
        self.SectionVolume_Inside = [round(volume, 2) for volume in Volume_Inside_List]
        return sum(Volume_Inside_List)

    def Styrofoam_Volume(self, SwDFunction_List):
        # If user select to design the canoe with no Cover.
        if (float(self.CoverLength) == float(0)): return 0

        if (self.Log[2] == 24):
            # minus the B2
            self.Length[1] = self.Length[1] - self.B2
        len_sum = self.GetLengthList(self.Length)[1:]  # don't need 0
        if (len(len_sum) == 1):
            # symmetric hall
            len_sum = [len_sum[0] / 2, len_sum[0]]
            operation_f = self.LocateCover(self.CoverLength, len_sum)
            # avoid Out Error
            operation_e = operation_f + []
            operation_e[0][1] = self.CoverLength  # can be configured
            Volume_FrontCover = self.Styrofoam_Volume_Calculate(operation_f, SwDFunction_List)
            Volume_EndCover = self.Styrofoam_Volume_Calculate(operation_e, SwDFunction_List)
        else:
            operation_f = self.LocateCover(self.CoverLength, len_sum)
            operation_e = self.LocateCover(len_sum[-1] - self.CoverLength, len_sum)
            Volume_FrontCover = self.Styrofoam_Volume_Calculate(operation_f, SwDFunction_List)
            Volume_EndCover = self.Volume_Inside - self.Styrofoam_Volume_Calculate(operation_e, SwDFunction_List)

        if (self.Log[2] == 24):
            # Redo the B2
            self.Length[1] = self.Length[1] + self.B2

        return (Volume_EndCover + Volume_FrontCover)

    def Styrofoam_Volume_Calculate(self, op_list, SwDFunction_List):
        volume = 0
        for op in op_list:
            if (op[1] == 0):
                pass  # save time
            elif (self.Log[2] != 24):
                # canoe that are not asymmetric
                if (self.WidthFList[op[0]] == -1 and self.DepthFList[op[0]] == -1):
                    volume += op[1] * 2 * \
                              quad(SwDFunction_List[op[0]], 0, self.Depth[op[0]])[0]
                elif (self.WidthFList[op[0]] != -1 and self.DepthFList[op[0]] != -1):
                    volume += 2 * ((self.ECurveF[op[0]]) / (self.ECurveF[op[0]] + 1)) * \
                              quad(SwDFunction_List[op[0]], 0, op[1])[0]
            else:
                if (op[0] == 1):
                    volume += 2 * ((self.ECurveF[op[0]]) / (self.ECurveF[op[0]] + 1)) * self.Depth[op[0]] * \
                              quad(self.WidthFList[op[0]], self.B2, op[1] + self.B2)[0]

                else:
                    volume += 2 * ((self.ECurveF[op[0]]) / (self.ECurveF[op[0]] + 1)) * \
                              quad(SwDFunction_List[op[0]], 0, op[1])[0]
        return volume

    def WaterLine_Caculation(self):
        self.WaterLine_TotalCrew = self.WaterLine_Approximate(self.TotalWeight)
        self.WaterLine_HalfCrew = self.WaterLine_Approximate(self.TotalWeight/2)
        self.WaterLine_NoneCrew = self.WaterLine_Approximate(self.CanoeWeight)

    def WaterLine_Approximate(self, weight):
        def margin_median(left, right):
            return (right-left)/2

        # Median Depth
        approx_depth = (self.Depth[0] + self.Thickness)/2
        approx_weight = self.Depth_Aspect_Capability_Acqurie(approx_depth)
        # Binary-method finding
        left_margin = 0
        right_margin = self.Depth[0] + self.Thickness

        while(not abs(weight - approx_weight) <= 0.1):
            if(approx_weight < weight):
                left_margin = approx_depth
                approx_depth = margin_median(left_margin,right_margin)
            elif(approx_weight > weight):
                right_margin = approx_depth
                approx_depth = margin_median(left_margin,right_margin)

        return approx_depth

    def Depth_Aspect_Capability_Acqurie(self, depth):
        # Constant is created with the simplifying of the formula, the constant in the front of integral.
        # Since the Depth_Aspect_Capability_calculation use different formula for constant and changing
        # Thus, constant1 represent constant_section's constant
        # constant2 represent changing_section's constant

        """
         self.Length[index] + self.B2_Diff - self.B2_O = Length of mid section of asymmetric hull

        """

        sum_capability = 0
        for num in range(len(self.Depth)):
            if(num != 1):
                length = self.Length[num] + self.Thickness
                #constant2
                constant = (2 * (self.SemiWidth[num] + self.Thickness) * (length))\
                           /((self.EWidthF[num]+1)*((self.Depth[num]+self.Thickness)**(1/self.ECurveF[num])))
                depth_aspect_integral = self.BuildLambda_Depth_Aspect_Integral_NonConstant(num)
                sum_capability += constant*quad(depth_aspect_integral,0,depth)[0]
            elif(num == 1):
                length = self.Length[num] if not self.Log[2] == 24 else self.Length[num] + self.B2_Diff - self.B2_O
                if(self.Log[2] == 24):
                    # constant2
                    constant = (2 * (self.SemiWidth[num] + self.Thickness) * (length)) \
                               / ((self.EWidthF[num] + 1) * (
                                (self.Depth[num] + self.Thickness) ** (1 / self.ECurveF[num])))
                    depth_aspect_integral = self.BuildLambda_Depth_Aspect_Integral_NonConstant(num)
                    sum_capability += constant * quad(depth_aspect_integral, 0, depth)[0]
                else:
                    #constant1
                    constant = (2*length*(self.SemiWidth[num]+self.Thickness))/\
                               ((self.EWidthF[num]+1)*((self.Depth[num]+self.Thickness)**(1/self.ECurveF[num])))
                    depth_aspect_integral = self.BuildLambda_Depth_Aspect_Integral_Constant(num)
                    sum_capability += constant * quad(depth_aspect_integral, 0, depth)[0]


        return sum_capability


    def Surfacearea(self):
        # Reassign the thickness to the 1/2 of thickness and recalculate the outside formulas for the surface Area
        save = self.Thickness
        self.Thickness = self.Thickness/2
        self.SignFunction_Main()

        self.SurfaceArea_Calculation()


        # Redo the Assign
        self.Thickness = save
        self.SignFunction_Main()


    def SurfaceArea_Calculation(self):
        # SurfaceArea Calculation algorithm use approximation method to calculate the arc length of the cross
        # section of canoe per 0.1 inches The arc length is calculated by the arc length formula through
        # scipy.integrate.quad By sum the calculated arc length, the total surface area is acquired.
        interval = 0.1

        for num in range(self.Num):
            print(f"Surface Num is {num}")
            # get width, depth at that index by using the self.WidthFlist, then get the length, add up
            CrossSection_SurfaceArea_Sum = 0
            if(self.Log[2] == 24 and num ==1):
                for lengthIndex in np.arange(self.B2_O, self.Length[num]+self.B2_Diff, interval):
                    formula, high_range = self.BuildLambda_ArcLength_Formula(num, lengthIndex)
                    if(formula == 0):
                        CrossSection_SurfaceArea_Sum +=0
                    else:
                        CrossSection_SurfaceArea_Sum += self.ArcLength(formula, 0,high_range)
                formula, high_range = self.BuildLambda_ArcLength_Formula(num, self.Length[num]+self.B2_Diff)
                CrossSection_SurfaceArea_Sum += self.ArcLength(formula, 0,high_range)* interval

            elif(self.WidthFList[num] == -1 and self.DepthFList[num] == -1 and self.WidthFList_Outside[num] == -1 and
                        self.DepthFList_Outside[num] == -1):
                formula, high_range = self.BuildLambda_ArcLength_Constant_Formula(num)
                if(formula ==0):
                    CrossSection_SurfaceArea_Sum +=0
                else:
                    CrossSection_SurfaceArea_Sum += self.Length[num] * self.ArcLength(formula, 0, high_range)

            else:
                for lengthIndex in np.arange(0, self.Length[num] + self.Thickness,interval):

                    formula, high_range = self.BuildLambda_ArcLength_Formula(num, lengthIndex)
                    if (formula == 0):
                        CrossSection_SurfaceArea_Sum += 0

                    else:

                        CrossSection_SurfaceArea_Sum += self.ArcLength(formula, 0,high_range) * interval

                formula, high_range = self.BuildLambda_ArcLength_Formula(num, self.Length[num] + self.Thickness)
                CrossSection_SurfaceArea_Sum += self.ArcLength(formula, 0, high_range)


            self.SurfaceArea_Section.append(CrossSection_SurfaceArea_Sum)

        self.SurfaceArea = sum(self.SurfaceArea_Section)

    def BuildLambda_Depth_Aspect_Integral_NonConstant(self, num):
        exp_a = 1/self.ECurveF[num]
        exp_b = 1/self.EWidthF[num]
        return lambda x: (x**exp_a)*(1-((x-self.Depth[num]-self.Thickness)
                                        /(self.Depth[num]+self.Thickness))**exp_b)
    def BuildLambda_Depth_Aspect_Integral_Constant(self, num):
        exp_a = 1/self.ECurveF[num]
        return lambda x: (x**exp_a)

    def BuildLambda_ArcLength_Formula(self, num, lengthIndex):
        width = self.WidthFList_Outside[num](lengthIndex)
        depth = self.DepthFList_Outside[num](lengthIndex) if type(self.DepthFList_Outside[num]) not in [int,float] else self.Depth[num]

        if(depth == 0):
            return 0,0
        exponent = self.ECurveF[num]
        coefficient = (depth * exponent)/(width**exponent)

        return lambda x: (1+(coefficient**2)*(x**(2*(exponent-1))))**(1/2), width

    def BuildLambda_ArcLength_Constant_Formula(self, num):
        width = self.SemiWidth[num]+self.Thickness
        depth = self.Depth[num]+self.Thickness
        if (depth == 0):
            return 0,0
        exponent = self.ECurveF[num]
        coefficient = (depth * exponent) / (width ** exponent)
        return lambda x: (1+(coefficient**2)*(x**(2*(exponent-1))))**(1/2), width

    def ArcLength(self, arc_length_formula, low_range, high_range):
        return 2 * quad(arc_length_formula, low_range, high_range)[0]


    # Helper Function
    @staticmethod
    def LocateCover(canoe_cover, length_list):
        """
        Take coverValue and return list of operation for calculation of volume
        """
        calculation_operation_list = []
        for lenIndex in range(1, len(length_list)):
            if (length_list[lenIndex] >= canoe_cover >= length_list[lenIndex - 1]):
                for index in [lenIndex - 1, lenIndex]:
                    if (canoe_cover >= length_list[index]):
                        calculation_operation_list.append([index, length_list[lenIndex - 1]])
                        canoe_cover = canoe_cover - length_list[lenIndex - 1]
                    else:
                        calculation_operation_list.append([index, canoe_cover])
            elif (canoe_cover < length_list[0] and lenIndex - 1 == 0):
                return [[0, canoe_cover]]  # if the cover is less than the first length

        return calculation_operation_list
