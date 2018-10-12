# -- coding: utf-8 --

from os2mo_data_import import Organisation, ImportUtility


def example_import():
    """
    Run the example to import the fictional organisation Magenta.

    """

    # The Organisation class is the main entry point,
    # It exposes the related sub classes such as:
    # Facet, Klasse, Itsystem, OrganisationUnit, Employee
    Magenta = Organisation(
        name="Magenta Aps",
        user_key="Magenta",
        municipality_code=101,
        create_defaults=True
    )

    # Add klasse with reference to facet "Enhedstype"
    Magenta.Klasse.add(
        identifier="Hovedenhed",  # User defined identifier
        facet_type_ref="Enhedstype",  # Belongs to facet: Enhedstype
        user_key="D1ED90C5-643A-4C12-8889-6B4174EF4467",  # User key for internal reference
        title="Hovedenhed"  # This is the displayed value
    )

    Magenta.Klasse.add(
        identifier="Afdeling",
        facet_type_ref="Enhedstype",
        user_key="91154D1E-E7CA-439B-B910-D4622FD3FD21",
        title="Afdeling"
    )

    # Root unit: Magenta
    # Belongs to unit type: "Hovedenhed"
    Magenta.OrganisationUnit.add(
        identifier="Magenta",
        name="Magenta Aps",
        org_unit_type_ref="Hovedenhed",  # Reference to the unit type
        date_from="1986-01-01"
    )

    # Use parent_ref to make it a sub group of "Magenta"
    Magenta.OrganisationUnit.add(
        identifier="Pilestræde",
        org_unit_type_ref="Afdeling",  # This unit is of type: Afdeling
        parent_ref="Magenta",  # Sub unit of/Belongs to Magenta
        date_from="1986-01-01"
    )

    Magenta.OrganisationUnit.add(
        identifier="SJA2",
        org_unit_type_ref="Afdeling",
        parent_ref="Magenta",  # Sub unit of/Belongs to Magenta
        date_from="1986-01-01"
    )

    # HOTFIX: nested units are failing
    # This will 'really' be fixed in the refactoring state

    # Adding sub units to the example
    Magenta.OrganisationUnit.add(
        identifier="Sysadmins",
        org_unit_type_ref="Afdeling",
        parent_ref="SJA2",  # Sub unit of/Belongs to SJA2
        date_from="1986-01-01"
    )

    Magenta.OrganisationUnit.add(
        identifier="Dummy",
        org_unit_type_ref="Afdeling",
        parent_ref="Sysadmins",  # Sub unit of/Belongs to SJA2
        date_from="1986-01-01"
    )

    # Address types for Organisation Unit
    Magenta.OrganisationUnit.add_type_address(
        owner_ref="Magenta",
        uuid="0a3f50c4-379f-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-01-01",
    )

    Magenta.OrganisationUnit.add_type_address(
        owner_ref="Magenta",
        value="00112233",
        address_type_ref="EAN",
        date_from="1986-01-01",
    )

    Magenta.OrganisationUnit.add_type_address(
        owner_ref="Magenta",
        value="11223344",
        address_type_ref="Telefon",
        date_from="1986-01-01",
    )


    # Create employees
    Magenta.Employee.add(
        identifier="Susanne Chæf",
        cpr_no="0101862233"
    )

    Magenta.Employee.add(
        identifier="Odin Perskov",
        cpr_no="0102862234"
    )

    Magenta.Employee.add(
        identifier="Ronja Rwander",
        cpr_no="0103862234"
    )

    Magenta.Employee.add(
        identifier="Jens Mortensen",
        cpr_no="0104862235"
    )

    Magenta.Employee.add(
        identifier="Bolette Buhl",
        cpr_no="0105862235"
    )

    Magenta.Employee.add(
        identifier="Carl Sand Holth",
        cpr_no="0106862235"
    )


    # Create job functions and assign to employees

    # Add job functions
    Magenta.Klasse.add(
        identifier="Direktør",
        facet_type_ref="Stillingsbetegnelse",
        user_key="Direktør",
        title="Direktør"
    )

    Magenta.Klasse.add(
        identifier="Projektleder",
        facet_type_ref="Stillingsbetegnelse",
        user_key="Projektleder",
        title="Projektleder"
    )

    Magenta.Klasse.add(
        identifier="Udvikler",
        facet_type_ref="Stillingsbetegnelse",
        user_key="Udvikler",
        title="Udvikler"
    )

    Magenta.Klasse.add(
        identifier="Projektmedarbejder",
        facet_type_ref="Stillingsbetegnelse",
        user_key="Projektmedarbejder",
        title="Projektmedarbejder"
    )

    # Assign job functions
    Magenta.Employee.add_type_engagement(
        owner_ref="Susanne Chæf",
        org_unit_ref="Magenta",
        job_function_ref="Direktør",
        engagement_type_ref="Ansat",
        date_from="1986-01-01"
    )

    Magenta.Employee.add_type_engagement(
        owner_ref="Odin Perskov",
        org_unit_ref="Pilestræde",
        job_function_ref="Projektleder",
        engagement_type_ref="Ansat",
        date_from="1986-02-01"
    )

    Magenta.Employee.add_type_engagement(
        owner_ref="Ronja Rwander",
        org_unit_ref="SJA2",
        job_function_ref="Projektleder",
        engagement_type_ref="Ansat",
        date_from="1986-03-01"
    )

    Magenta.Employee.add_type_engagement(
        owner_ref="Jens Mortensen",
        org_unit_ref="Pilestræde",
        job_function_ref="Udvikler",
        engagement_type_ref="Ansat",
        date_from="1986-04-01"
    )

    Magenta.Employee.add_type_engagement(
        owner_ref="Bolette Buhl",
        org_unit_ref="SJA2",
        job_function_ref="Udvikler",
        engagement_type_ref="Ansat",
        date_from="1986-05-01"
    )

    Magenta.Employee.add_type_engagement(
        owner_ref="Carl Sand Holth",
        org_unit_ref="Pilestræde",
        job_function_ref="Projektmedarbejder",
        engagement_type_ref="Ansat",
        date_from="1986-06-01"
    )

    # Add association
    Magenta.Klasse.add(
        identifier="Ekstern Konsulent",
        facet_type_ref="Tilknytningstype",
        user_key="Ekstern Konsulent",
        title="Ekstern Konsulent"
    )

    Magenta.Employee.add_type_association(
        owner_ref="Carl Sand Holth",
        org_unit_ref="Pilestræde",
        job_function_ref="Projektmedarbejder",
        association_type_ref="Ekstern Konsulent",
        address_uuid="0a3f50c4-379f-32b8-e044-0003ba298018",
        date_from="1986-10-01"
    )


    # Add addresses
    Magenta.Employee.add_type_address(
        owner_ref="Susanne Chæf",
        uuid="0a3f50a0-ef5a-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-11-01",
    )

    Magenta.Employee.add_type_address(
        owner_ref="Odin Perskov",
        uuid="0a3f50a0-ef5a-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-11-01",
    )

    Magenta.Employee.add_type_address(
        owner_ref="Ronja Rwander",
        uuid="0a3f50a0-ef5a-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-11-01",
    )

    Magenta.Employee.add_type_address(
        owner_ref="Jens Mortensen",
        uuid="0a3f50a0-ef5a-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-11-01",
    )

    Magenta.Employee.add_type_address(
        owner_ref="Bolette Buhl",
        uuid="0a3f50a0-ef5a-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-11-01",
    )

    Magenta.Employee.add_type_address(
        owner_ref="Carl Sand Holth",
        uuid="0a3f50a0-ef5a-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-11-01",
    )


    # Add roles and assign to employees
    Magenta.Klasse.add(
        identifier="Medarbejder repræsentant",
        facet_type_ref="Rolletype",
        user_key="Medarbejder repræsentant",
        title="Medarbejder repræsentant"
    )

    Magenta.Klasse.add(
        identifier="Nøgleansvarlig",
        facet_type_ref="Rolletype",
        user_key="Nøgleansvarlig",
        title="Nøgleansvarlig"
    )

    Magenta.Employee.add_type_role(
        owner_ref="Susanne Chæf",
        org_unit_ref="Magenta",
        role_type_ref="Nøgleansvarlig",
        date_from="1986-12-01"
    )

    Magenta.Employee.add_type_role(
        owner_ref="Bolette Buhl",
        org_unit_ref="SJA2",
        role_type_ref="Medarbejder repræsentant",
        date_from="1986-12-01"
    )

    Magenta.Employee.add_type_role(
        owner_ref="Jens Mortensen",
        org_unit_ref="Pilestræde",
        role_type_ref="Medarbejder repræsentant",
        date_from="1986-12-01"
    )

    # Create manager type, level and responsibilites
    # and assign to employee

    # Manager type
    Magenta.Klasse.add(
        identifier="Direktør",
        facet_type_ref="Ledertyper",
        user_key="Direktør",
        title="Virksomhedens direktør"
    )

    # Manager level
    Magenta.Klasse.add(
        identifier="Højeste niveau",
        facet_type_ref="Lederniveau",
        user_key="Højeste niveau",
        title="Højeste niveau"
    )

    # Add responsabilities
    Magenta.Klasse.add(
        identifier="Tage beslutninger",
        facet_type_ref="Lederansvar",
        user_key="Tage beslutninger",
        title="Tage beslutninger"
    )

    Magenta.Klasse.add(
        identifier="Motivere medarbejdere",
        facet_type_ref="Lederansvar",
        user_key="Motivere medarbejdere",
        title="Motivere medarbejdere"
    )

    Magenta.Klasse.add(
        identifier="Betale løn",
        facet_type_ref="Lederansvar",
        user_key="Betale løn",
        title="Betale løn"
    )

    Magenta.Employee.add_type_manager(
        owner_ref="Susanne Chæf",
        org_unit_ref="Magenta",
        manager_type_ref="Direktør",
        manager_level_ref="Højeste niveau",
        responsibility_list=["Tage beslutninger", "Motivere medarbejdere", "Betale løn"],
        date_from="1986-12-01",
    )


    # Leave of absence (Does not work after release 0.10)
    # Leave type requires an exisiting engagement type

    # Magenta.Klasse.add(
    #     identifier="Sygeorlov",
    #     facet_type_ref="Orlovstype",
    #     user_key="Sygeorlov",
    #     title="Sygeorlov"
    # )
    #
    # Magenta.Employee.add_type_leave(
    #     owner_ref="Jens Mortensen",
    #     leave_type_ref="Sygeorlov",
    #     date_from="2018-01-22",
    #     date_to="2018-11-02"
    # )
    #
    # Magenta.Employee.add_type_leave(
    #     owner_ref="Bolette Buhl",
    #     leave_type_ref="Sygeorlov",
    #     date_from="2018-01-22",
    #     date_to="2018-11-02"
    # )

    # Create IT system and assign to employee

    Magenta.Itsystem.add(
        identifier="Servermiljø",
        system_name="Servermiljø"
    )

    Magenta.Employee.add_type_itsystem(
        owner_ref="Jens Mortensen",
        user_key="jmort",
        itsystem_ref="Servermiljø",
        date_from="1987-10-01"
    )

    Magenta.Employee.add_type_itsystem(
        owner_ref="Bolette Buhl",
        user_key="bolbu",
        itsystem_ref="Servermiljø",
        date_from="1987-10-01"
    )

    # Import everything into running instance
    # Requires an actual running instance
    os2mo = ImportUtility(dry_run=False)
    os2mo.import_all(Magenta)


if __name__ == "__main__":
    example_import()
