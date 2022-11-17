data = Drop[Import["/path/to/file.csv", "Data"], 1];

plotFunction[x_, y_] := GeoRegionValuePlot[ZIPTuples, ImageSize -> Medium, PlotStyle -> Directive[EdgeForm[]], GeoRange -> x, GeoRangePadding -> Scaled[y], GeoProjection -> "Mercator", GeoZoomLevel -> 6]

(*Mapping the entire U.S. base map*)
plotFunction[Entity["Country", "UnitedStates"], 0.1]

(* ! Run the following code only after running the above ! *)

(*Plug a city of your choice here*)
plotFunction[#, 1] & /@ {FullForm[Entity["City", {"Greensboro", "NorthCarolina", "UnitedStates"}]]}