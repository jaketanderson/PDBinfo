import freesasa
from main import *


def protonate(original_tweet, filename):

    try:
        sp.run(
            f"obabel -ipdb {path}{filename}.pdb -opdb {path}{filename}.pdb -p 7.4",
            shell=True,
        )

    except:
        client.create_tweet(
            in_reply_to_tweet_id=original_tweet.id,
            text=f"Openbabel was unable to protonate pdb {filename} in preparation for calculations. To try again without protonation, add the flag -noprot to your next tweet.",
        )
        return False

    return True


def get_sasa(original_tweet, filename):

    nslices = 1000
    if "-s " in original_tweet.text:
        start = text.find("-s ") + len("-s ")

        try:
            end = start
            while text[end].isnumeric():
                end += 1
            nslices = int(text[start : end + 1])
            assert 1 <= nslices <= 5000

        except:
            client.create_tweet(
                in_reply_to_tweet_id=original_tweet.id,
                text=f"There was an error with your specified number of slices for the SASA calculation. Please use format: -s [integer st. 1<=integer<=5000]",
            )
            return False

    try:
        structure = freesasa.Structure(f"{path}{filename}.pdb")
        result = freesasa.calc(
            structure,
            freesasa.Parameters(
                {"algorithm": freesasa.LeeRichards, "n-slices": nslices}
            ),
        )
        area_classes = freesasa.classifyResults(result, structure)

        text = f"SASA for {filename} in square nm:\n\n"
        text = text + "Total : {:.8e}".format(result.totalArea() / 10)

        for key in area_classes:
            text = text + "\n" + str(key) + ": {:.8e}".format(area_classes[key] / 10)

        client.create_tweet(in_reply_to_tweet_id=original_tweet.id, text=text)
        return True

    except:
        client.create_tweet(
            in_reply_to_tweet_id=original_tweet.id,
            text=f"Error calculating SASA for {filename}.",
        )
        return False
