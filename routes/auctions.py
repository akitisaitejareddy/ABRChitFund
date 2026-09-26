from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import login_required

from models.group import ChitGroup

from services.auction_service import (
    get_all_auctions,
    get_group_members,
    create_auction,
    delete_auction
)



auctions = Blueprint(
    "auctions",
    __name__,
    url_prefix="/auctions"
)



# -------------------------------------------------
# Auction List
# -------------------------------------------------

@auctions.route("/")
@login_required
def list_auctions():

    auctions_list = get_all_auctions()

    return render_template(
        "auctions/list.html",
        auctions=auctions_list
    )



# -------------------------------------------------
# Get Group Members API
# -------------------------------------------------

@auctions.route(
    "/group/<int:group_id>/members"
)
@login_required
def group_members(group_id):

    members = get_group_members(
        group_id
    )


    return jsonify([

        {
            "id": member.id,
            "name": member.name,
            "mobile": member.mobile
        }

        for member in members

    ])




# -------------------------------------------------
# Create Auction
# -------------------------------------------------

@auctions.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    groups = ChitGroup.query.filter_by(

        status="ACTIVE"

    ).order_by(

        ChitGroup.name

    ).all()



    if request.method == "POST":


        data = {

            "group_id":
                request.form.get(
                    "group_id"
                ),


            "winner_customer_id":
                request.form.get(
                    "winner_customer_id"
                ),


            "auction_month":
                request.form.get(
                    "auction_month"
                ),


            "auction_date":
                request.form.get(
                    "auction_date"
                ),


            "bid_amount":
                request.form.get(
                    "bid_amount"
                )

        }



        try:

            create_auction(data)


            flash(
                "Auction completed successfully",
                "success"
            )


            return redirect(
                url_for(
                    "auctions.list_auctions"
                )
            )


        except ValueError as error:

            flash(
                str(error),
                "danger"
            )



    return render_template(

        "auctions/create.html",

        groups=groups

    )
    
# ---------------------------------
# Delete Auction
# ---------------------------------

@auctions.route(
    "/delete/<int:auction_id>",
    methods=["POST"]
)
@login_required
def delete(auction_id):

    try:

        delete_auction(
            auction_id
        )


        flash(
            "Auction deleted successfully",
            "success"
        )


    except ValueError as error:

        flash(
            str(error),
            "danger"
        )


    return redirect(
        url_for(
            "auctions.list_auctions"
        )
    )