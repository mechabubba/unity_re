from collections import OrderedDict
import itertools
import json
import math
import sys
from unityparser import UnityDocument

"""
honestly better off just using this if your editor supports it https://gist.github.com/karljj1/58f16e936d13a94ae6a2f741fd271d91
did not want to port this to unity 6 so instead i dumped it here
but atm it is so unfinished
"""

def handle_convert_particle_systems(args):
    # idk do somethin
    # will prob only allow this to take in one unity file at a time
    print("@todo make the attachment")
    pass

def convert_particle_systems(class_name):
    entries = doc.filter(class_names=("GameObject",), attributes=("m_Name",))
    for entry in entries:
        if entry.m_Name == "Stars": # this is the parent gameobject
            data = extract(entry)
            print(json.dumps(data, indent=4))
            break

"""
stars components look like
[
  OrderedFlowDict({'4': OrderedFlowDict({'fileID': '3108'})}),
  OrderedFlowDict({'15': OrderedFlowDict({'fileID': '5378'})}),
  OrderedFlowDict({'12': OrderedFlowDict({'fileID': '5377'})}),
  OrderedFlowDict({'26': OrderedFlowDict({'fileID': '6826'})})
]
"""

def entry_by_fileID(object_class, fileID):
    entries = doc.filter(class_names=(object_class,))
    for entry in entries:
        #print(entry.anchor)
        if entry.anchor == fileID:
            return entry
    return None

def extract(stars):
    data = {}

    for comp in stars.m_Component:
        for k, v in comp.items():
            k = int(k)
            match k:
                case 4:
                    # Transform
                    e = entry_by_fileID("Transform", v["fileID"])
                    if e is not None:
                        d = extract_transform(e);
                        data["transform"] = extract_transform(e)
                    else:
                        print("entry is none... transform not found")
                        print("Transform", v["fileID"])
                        print()
                        sys.exit(1)

                case 15:
                    # EllipsoidParticleEmitter
                    e = entry_by_fileID("EllipsoidParticleEmitter", v["fileID"])
                    if e is not None:
                        d, u = extract_epe(e)
                        for k, v in d.items():
                            data[k] = v

                case 12:
                    # ParticleAnimator
                    e = entry_by_fileID("ParticleAnimator", v["fileID"])
                    if e is not None:
                        d = extract_psa(e)
                        for k, v in d.items():
                            data[k] = v

                case 26:
                    # ParticleRenderer
                    e = entry_by_fileID("ParticleRenderer", v["fileID"])
                    if e is not None:
                        d = extract_psr(e)
                        for k, v in d.items():
                            data[k] = v

                case _:
                    print("[!!!] unknown/unimplemented m_Component type?", k)

    return data

def min_max_curve(_min, _max):
    if math.isclose(_min, _max):
        return f"ParticleSystem.MinMaxCurve({_min})"
    else:
        return f"ParticleSystem.MinMaxCurve({_min}, {_max})"

def extract_transform(entry):
    data = {}
    data["Local Rotation"] = entry.m_LocalRotation
    data["Local Position"] = entry.m_LocalPosition
    data["Local Scale"] = entry.m_LocalScale
    return data

def extract_epe(entry):
    print(entry)

    data = {}
    unsorted = {}

    # Main
    main = {}
    main["Start Speed"] = float(0) # hardcoded
    main["Max Particles"] = 10000  # hardcoded, no max set in original yaml
    main["Play On Awake"] = bool(entry.m_Emit)
    main["Start Size"] = min_max_curve(float(entry.minSize), float(entry.maxSize))
    main["Start Lifetime"] = min_max_curve(float(entry.minEnergy), float(entry.maxEnergy))
    main["Duration"] = float(entry.maxEnergy)
    main["Start Rotation"] = min_max_curve(float(0.0), math.radians(360) if bool(entry.rndRotation) else float(0.0))
    main["Loop"] = False # hardcoded, could change later
    main["Simulation Space"] = "World" if bool(getattr(entry, "Simulate in Worldspace?")) else "Local"
    main["Scaling Mode"] = "Shape" # hardcoded

    # Emission
    ems = {}
    if bool(entry.m_OneShot):
        main["Loop"] = True
        ems["Rate over Time"] = 0
        ems["Burst Count"] = 1 # UNITY_2017_2_OR_NEWER

        burst = {}
        burst["Cycle Count"] = 1
        burst["Cycle Count"] = (2 ** 31) - 1 # ???
        burst["Repeat Interval"] = "main['Start Lifetime'].constantMax"

        #if UNITY_2017_2_OR_NEWER
        burst["Count"] = min_max_curve(float(entry.minEmission), float(entry.maxEmission))
        #else
        #    burst.maxCount = (short)maxEmission;
        #    burst.minCount = (short)minEmission;
        #    emission.SetBursts(new[] { burst });
        #endif

        ems["_bursts"] = [burst]
    else:
        ems["Rate Over Time"] = min_max_curve(float(entry.minEmission), float(entry.maxEmission))

    # Inherit velocity
    iv = {}
    if not math.isclose(float(entry.emitterVelocityScale), 0):
        iv["Enabled"] = True
        iv["Curve"] = float(entry.emitterVelocityScale)

    # Velocity over lifetime

    # dont want to do this because it requires a vector math library and i dont have numpy installed
    # for now, the velocities of everything i'm looking at are 0.
    # this resolves to whatever the defaults are for 'Velocity over Lifetime'
    # https://gist.github.com/karljj1/58f16e936d13a94ae6a2f741fd271d91#file-legacy_particle_system_updater-cs-L373-L419

    #mag_sqr = lambda o : (o.x * o.x) + (o.y * o.y) + (o.z + o.z)
    #min_vel = None
    #max_vel = None
    #if mag_sqr(entry.localVelocity) > sys.float_info.epsilon:
    #    pass

    # Rotation over lifetime
    # also ignoring this one because it doesn't apply to me and dont want to do a new thing
    # https://gist.github.com/karljj1/58f16e936d13a94ae6a2f741fd271d91#file-legacy_particle_system_updater-cs-L421-L427
    rol = "see comments"
    if float(entry.rndAngularVelocity) > sys.float_info.epsilon:
        rol["Enabled"] = True
        #rotationOverLifetime.z = new ParticleSystem.MinMaxCurve(Mathf.Deg2Rad * angularVelocity, new AnimationCurve(new Keyframe(0f, 0f), new Keyframe(1f, 1f)));

    # Shape
    # by being in this function we're implicitly an Ellipsoid
    # if you're not using an EllipsoidParticleEmitter you probably got a weird error you need to diagnose anyway, so go do that
    shape = {}
    #print(entry.m_Ellipsoid)
    el = [float(entry.m_Ellipsoid[a]) for a in ["x", "y", "z"]] # this is stupid
    #print(el)
    max_dim = max(el[0], el[1], el[2])
    print(max_dim)
    if max_dim > 0:
        shape["Enabled"] = True
        shape["Shape Type"] = "Sphere"
        shape["Radius"] = max_dim
        shape["Scale"] = (el[0] / max_dim, el[1] / max_dim, el[2] / max_dim)

    data["particle_system"] = main
    data["emission"] = ems
    data["inherit_velocity"] = iv
    data["rotation_over_lifetime"] = rol
    data["shape"] = shape

    # random stuff
    unsorted["shape:Enabled"] = False # set elsewhere

    return data, unsorted

def extract_psa(entry):
    data = { "comment": "see comments" }

    # skipping around on this one too
    # - no linear or random force > no Force over Lifetime
    # - sizeGrow = 0 > no Size over Lifetime
    # - autodestruct = 0 > no Stop action
    # - damping = 0 > (1 < 1.0f) == false > no dampening of velocityOverLifetime

    # do have to worry about color.... which maps to Color over Lifetime

    # color is just keyed uniformly between 0 and 1 inclusive
    # so in my case, i have five keys;
    # 184549375 > 3036676095 > 4294967295 > 3036676095 > 184549375 (rgba format, convert to hex and pad front with zeros as needed)

    return { "animation": data }

# these are mapped to what they were in unity 3.5.3, roughly where im porting from
ParticleSystemRenderMode = {
    "Billboard": 0,
    "Stretch": 1,
    "SortedBillboard": 2,
    "HorizontalBillboard": 3,
    "VerticalBillboard": 4
}

def extract_psr(entry):
    data = {}

    renderer = {}
    match entry.m_StretchParticles:
        # deduced these values from the unity 350 docs and the gist
        case 0:
            renderer["Render Mode"] = "Billboard"
        case 1:
            renderer["Render Mode"] = "Stretch"
        case 2:
            renderer["Render Mode"] = "Billboard"
            renderer["Sort Mode"] = "Distance"
        case 3:
            renderer["Render Mode"] = "Horizontal Billboard"
        case 4:
            renderer["Render Mode"] = "Vertical Billboard"
        case _:
            print("mystery render mode detected. abort mission!")

    renderer["Camera Velocity Scale"] = float(entry.m_CameraVelocityScale)
    renderer["Length Scale"] = float(entry.m_LengthScale)
    renderer["Velocity Scale"] = float(entry.m_VelocityScale)
    renderer["Max Particle Size"] = float(entry.m_MaxParticleSize)

    renderer["Cast Shadows"] = entry.m_CastShadows # this was "shadowCastingMode" - not an exact match
    renderer["Receive Shadows"] = entry.m_ReceiveShadows
    renderer["Material"] = entry.m_Materials # this was "sharedMaterial" - not an exact match

    # uv maps to texture sheet animation
    uv = {}
    anim = getattr(entry, "UV Animation")
    x = int(getattr(anim, "x Tile", 0))
    y = int(getattr(anim, "y Tile", 0))
    cycles = float(getattr(anim, "cycles", 0))

    if x > 1 or y > 1:
        uv["Enabled"] = True
        uv["Num Tiles X"] = x
        uv["Num Tiles Y"] = y
        uv["Cycle Count"] = cycles

    renderer["texture_sheet_animation"] = uv
    data["renderer"] = renderer

    return data
